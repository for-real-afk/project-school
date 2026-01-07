from fastapi import APIRouter, Request, Body, HTTPException
from models import Chat
from datetime import datetime
from langchain_core.messages import HumanMessage
from pydantic import BaseModel

class AssignmentRequest(BaseModel):
    userId: str

router = APIRouter()

@router.post("/assign", status_code=201)
async def run_assignment_workflow(request: Request, payload: AssignmentRequest):
    # Now Swagger will show {"userId": "string"} instead of additionalProp1
    db = request.app.state.db
    user_id = payload.userId
    agent = request.app.state.agent

    if not user_id:
        raise HTTPException(status_code=400, detail="userId is required")

    # 1. Prepare State for the Multi-Node Agent
    initial_state = {
        "userId": user_id,
        "message": "/assign",
        "messages": [HumanMessage(content="Triggering task assignment")],
        "goals": [],
        "response_text": ""
    }

    # 2. Run the Graph (Supervisor -> Planner -> Commit)
    final_state = await agent.ainvoke(initial_state)

    # 3. Store the result in Chat history so the user sees it
    agent_msg = {
        "userId": user_id,
        "userType": "agent",
        "message": final_state.get("response_text"),
        "timestamp": datetime.now()
    }
    await db.chats.insert_one(agent_msg)

    return {"status": "success", "agent_response": final_state.get("response_text")}