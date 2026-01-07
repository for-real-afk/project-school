from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Annotated, Sequence
from datetime import datetime
from bson import ObjectId
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class Project(BaseModel):
    model_config = ConfigDict(populate_by_name=True, json_encoders={ObjectId: str})
    id: Optional[str] = None
    name: str
    description: Optional[str] = None
    status: str = "active"
    created_at: datetime = Field(default_factory=datetime.now)

class Task(BaseModel):
    model_config = ConfigDict(populate_by_name=True, json_encoders={ObjectId: str})
    id: Optional[str] = None
    project_id: str
    title: str
    status: str = "pending"
    assigned_to: Optional[str] = None

class Chat(BaseModel):
    id: Optional[str] = None
    userId: str
    userType: str # "user" or "agent"
    message: str
    timestamp: datetime = Field(default_factory=datetime.now)

class Goal(BaseModel):
    userId: str
    goals: List[str]

# This is the TypedDict used by LangGraph to pass data between nodes
class AgentState(TypedDict):
    userId: str
    message: str
    # Annotated with add_messages so history persists correctly
    messages: Annotated[Sequence[BaseMessage], add_messages]
    goals: List[str]
    active_task: Optional[dict]
    # New fields for the multi-node logic
    project_pool: Optional[List[dict]] 
    selected_project_id: Optional[str]
    assigned_tasks: Optional[List[str]] 
    response_text: str
    next_action: Optional[str] # To help with routing logic

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    assigned_to: Optional[str] = None

class UserTaskLink(BaseModel):
    userId: str
    taskId: str #objectId