from fastapi import APIRouter, Request, Body, HTTPException
from datetime import datetime
from models import Chat, AgentState
from langchain_core.messages import HumanMessage
from bson import ObjectId

router = APIRouter()


def serialize(doc):
    """Helper to convert MongoDB _id to string id"""
    if not doc: return None
    doc["id"] = str(doc.pop("_id"))
    return doc


# @router.post("/agent", response_model=Chat, status_code=201)
# async def chat_with_agent(request: Request, chat_req: Chat = Body(...)):
#     db = request.app.state.db
#     agent = request.app.state.agent
#     user_id = chat_req.userId

#     # 1. Store the User's Message in History
#     user_chat_dict = chat_req.model_dump(exclude={"id"})
#     user_chat_dict["timestamp"] = datetime.now()
#     await db.chats.insert_one(user_chat_dict)

#     # 2. Prepare the Input for LangGraph
#     # We pass the current message as a HumanMessage for the LLM history
#     initial_state = {
#         "userId": user_id,
#         "message": chat_req.message,
#         "messages": [HumanMessage(content=chat_req.message)],
#         "goals": [],  # Will be populated by the 'analyze' node in agent
#         "active_task": None,  # Will be populated by the 'analyze' node in agent
#         "response_text": ""
#     }

#     # 3. Run the Agent Workflow
#     # The 'analyze' node inside the agent will fetch DB data using the db ref passed at init
#     try:
#         final_state = await agent.ainvoke(initial_state)
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Agent Error: {str(e)}")

#     # 4. Prepare and Store the Agent's Response
#     agent_msg_content = final_state.get("response_text", "I'm sorry, I couldn't process that.")

#     agent_chat_doc = {
#         "userId": user_id,
#         "userType": "agent",
#         "message": agent_msg_content,
#         "timestamp": datetime.now()
#     }

#     result = await db.chats.insert_one(agent_chat_doc)

#     # 5. Return the serialized agent message to the frontend
#     created_chat = await db.chats.find_one({"_id": result.inserted_id})
#     return serialize(created_chat)


# @router.get("/history/{user_id}", response_model=list[Chat])
# async def get_chat_history(request: Request, user_id: str):
#     db = request.app.state.db
#     cursor = db.chats.find({"userId": user_id}).sort("timestamp", 1)
#     return [serialize(doc) async for doc in cursor]

# @router.post("/assign", response_model=Chat, status_code=201)
# async def handle_assign_command(request: Request, chat_req: Chat = Body(...)):
#     db = request.app.state.db
#     agent = request.app.state.agent
    
#     # 1. Check if the message starts with /assign
#     if not chat_req.message.strip().lower().startswith("/assign"):
#         raise HTTPException(status_code=400, detail="This endpoint only handles /assign command")

#     # 2. Initialize State for the Multi-Node Agent
#     initial_state = {
#         "userId": chat_req.userId,
#         "message": chat_req.message,
#         "messages": [HumanMessage(content=chat_req.message)],
#         "goals": [],
#         "active_task": None,
#         "response_text": ""
#     }

#     # 3. Invoke the Multi-Node Agent
#     final_state = await agent.ainvoke(initial_state)

#     # 4. Save and Return the Result
#     agent_chat_doc = {
#         "userId": chat_req.userId,
#         "userType": "agent",
#         "message": final_state["response_text"],
#         "timestamp": datetime.now()
#     }
    
#     result = await db.chats.insert_one(agent_chat_doc)
#     created_chat = await db.chats.find_one({"_id": result.inserted_id})
#     return serialize(created_chat)