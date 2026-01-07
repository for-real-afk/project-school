from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from models import AgentState
from typing import Literal
import os
import json
from datetime import datetime


def get_learning_agent(db):
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash", # Stable production model
        temperature=0.2,
        google_api_key=os.getenv("GOOGLE_API_KEY")
    )

    # --- Node 1: Supervisor (Entry Point) ---
    async def supervisor_node(state: AgentState):
        user_id = state["userId"]
        # Fetch existing goals
        goals_doc = await db.goals.find_one({"userId": user_id})
        goals = goals_doc.get("goals", []) if goals_doc else []
        
        return {"goals": goals}

    # --- Routing Logic ---
    def router(state: AgentState) -> Literal["planner", "ask_for_goals"]:
        if not state.get("goals") or len(state["goals"]) == 0:
            return "ask_for_goals"
        return "planner"

    # --- Node 2: Ask for Goals (Fallback) ---
    async def ask_for_goals_node(state: AgentState):
        return {
            "response_text": "I see you haven't set any career goals yet. To assign the right tasks, please tell me: What are your career goals? (e.g., 'I want to become a Senior Backend Engineer')"
        }

    # --- Node 3: Task Planner (Gemini Alignment) ---
async def task_planner_node(state: AgentState):
    # 1. Fetch available projects
    cursor = db.projects.find({"status": "active"}).limit(5)
    projects = [p async for p in cursor]
    project_text = "\n".join([f"ID:{p['_id']} Name:{p['name']}" for p in projects])

    # 2. Gemini selects project and 5 tasks
    prompt = f"User Goals: {state['goals']}\nPool:\n{project_text}\nPick 1 project and generate 5 tasks. Return JSON: {{'project_id': '...', 'tasks': [{{'title': '...', 'desc': '...'}}]}}"
    
    response = await llm.ainvoke(prompt)
    # Parse the JSON from Gemini
    data = json.loads(response.content.replace("```json", "").replace("```", ""))

    # 3. Push to DB
    for task_item in data['tasks']:
        await db.tasks.insert_one({
            "project_id": data['project_id'],
            "title": task_item['title'],
            "description": task_item.get('desc', ''),
            "status": "pending",
            "assigned_to": state["userId"],
            "created_at": datetime.now()
        })

    return {"response_text": f"I've assigned 5 tasks from project {data['project_id']} to your dashboard."}

    # --- Graph Construction ---
    workflow = StateGraph(AgentState)
    
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("ask_for_goals", ask_for_goals_node)
    workflow.add_node("planner", task_planner_node)

    workflow.set_entry_point("supervisor")
    
    workflow.add_conditional_edges(
        "supervisor",
        router,
        {
            "ask_for_goals": "ask_for_goals",
            "planner": "planner"
        }
    )

    workflow.add_edge("ask_for_goals", END)
    workflow.add_edge("planner", END)

    return workflow.compile()