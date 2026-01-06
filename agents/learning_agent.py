from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage
from models import AgentState
import os
from dotenv import load_dotenv


# Load environment variables first
load_dotenv()




def get_learning_agent(db):
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found in environment variables")


    print(f"🔍 Using API Key: {api_key[:10]}...")  # Debug print


    # Use gemini-1.5-pro (most stable option)
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.7,
        google_api_key=api_key
    )


    print("✅ LLM initialized with model: gemini-1.5-pro")


    async def analyze_state(state: AgentState):
        user_id = state["userId"]
        goals_doc = await db.goals.find_one({"userId": user_id})
        task = await db.tasks.find_one({"assigned_to": user_id, "status": {"$ne": "completed"}})


        print(f"📊 Analyzed state for user: {user_id}")
        print(f"   Goals: {goals_doc['goals'] if goals_doc else []}")
        print(f"   Active task: {task['title'] if task else 'None'}")


        return {
            "goals": goals_doc["goals"] if goals_doc else [],
            "active_task": task
        }


    async def call_model(state: AgentState):
        goals = state.get('goals', [])
        active_task = state.get('active_task')


        system_msg = f"""You are a helpful learning mentor and project assistant.


User's Goals: {', '.join(goals) if goals else 'No goals set yet'}
Active Task: {active_task['title'] if active_task else 'No active tasks'}


Provide helpful, encouraging guidance to help the user achieve their goals and complete their tasks."""


        messages = [SystemMessage(content=system_msg)] + state["messages"]


        print(f"🤖 Calling LLM with {len(messages)} messages...")


        try:
            response = await llm.ainvoke(messages)
            print(f"✅ Got response: {response.content[:100]}...")
            return {"response_text": response.content, "messages": [response]}
        except Exception as e:
            print(f"❌ LLM Error: {str(e)}")
            raise


    workflow = StateGraph(AgentState)
    workflow.add_node("analyze", analyze_state)
    workflow.add_node("agent", call_model)
    workflow.set_entry_point("analyze")
    workflow.add_edge("analyze", "agent")
    workflow.add_edge("agent", END)


    return workflow.compile()

