from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Project Management API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "project_management")

client = None
db = None

class Project(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    status: str = Field(default="active")
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class Task(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    project_id: str
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    status: str = Field(default="pending")
    priority: str = Field(default="medium")
    assigned_to: Optional[str] = None
    due_date: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    assigned_to: Optional[str] = None
    due_date: Optional[datetime] = None

@app.on_event("startup")
async def startup_db_client():
    global client, db
    try:
        client = AsyncIOMotorClient(MONGODB_URL)
        db = client[DATABASE_NAME]
        await client.server_info()
        print(f"Connected to MongoDB: {DATABASE_NAME}")
        await db.projects.create_index("name")
        await db.projects.create_index("status")
        await db.tasks.create_index("project_id")
        print("Indexes created")
    except Exception as e:
        print(f"Error: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_db_client():
    global client
    if client:
        client.close()

def project_helper(project) -> dict:
    return {
        "id": str(project["_id"]),
        "name": project["name"],
        "description": project.get("description"),
        "status": project.get("status", "active"),
        "start_date": project.get("start_date"),
        "end_date": project.get("end_date"),
        "created_at": project.get("created_at"),
        "updated_at": project.get("updated_at")
    }

def task_helper(task) -> dict:
    return {
        "id": str(task["_id"]),
        "project_id": task["project_id"],
        "title": task["title"],
        "description": task.get("description"),
        "status": task.get("status", "pending"),
        "priority": task.get("priority", "medium"),
        "assigned_to": task.get("assigned_to"),
        "due_date": task.get("due_date"),
        "created_at": task.get("created_at"),
        "updated_at": task.get("updated_at")
    }

@app.get("/")
async def root():
    return {"message": "Project API with MongoDB", "version": "2.0.0"}

@app.post("/save-project", response_model=Project, status_code=201)
async def create_project(project: Project):
    project_dict = project.dict(by_alias=True, exclude={"id"})
    project_dict["created_at"] = datetime.now()
    project_dict["updated_at"] = datetime.now()
    result = await db.projects.insert_one(project_dict)
    created = await db.projects.find_one({"_id": result.inserted_id})
    return project_helper(created)

@app.get("/save-project", response_model=List[Project])
async def get_all_projects():
    projects = []
    cursor = db.projects.find({}).sort("created_at", -1)
    async for project in cursor:
        projects.append(project_helper(project))
    return projects

@app.get("/save-project/{project_id}", response_model=Project)
async def get_project(project_id: str):
    if not ObjectId.is_valid(project_id):
        raise HTTPException(status_code=400, detail="Invalid ID")
    project = await db.projects.find_one({"_id": ObjectId(project_id)})
    if not project:
        raise HTTPException(status_code=404, detail="Not found")
    return project_helper(project)

@app.put("/save-project/{project_id}", response_model=Project)
async def update_project(project_id: str, update: ProjectUpdate):
    if not ObjectId.is_valid(project_id):
        raise HTTPException(status_code=400, detail="Invalid ID")
    data = {k: v for k, v in update.dict(exclude_unset=True).items() if v is not None}
    if data:
        data["updated_at"] = datetime.now()
        await db.projects.update_one({"_id": ObjectId(project_id)}, {"$set": data})
    updated = await db.projects.find_one({"_id": ObjectId(project_id)})
    if not updated:
        raise HTTPException(status_code=404, detail="Not found")
    return project_helper(updated)

@app.delete("/save-project/{project_id}", status_code=204)
async def delete_project(project_id: str):
    if not ObjectId.is_valid(project_id):
        raise HTTPException(status_code=400, detail="Invalid ID")
    await db.tasks.delete_many({"project_id": project_id})
    result = await db.projects.delete_one({"_id": ObjectId(project_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Not found")

@app.post("/save-project-tasks", response_model=Task, status_code=201)
async def create_task(task: Task):
    if not ObjectId.is_valid(task.project_id):
        raise HTTPException(status_code=400, detail="Invalid project ID")
    task_dict = task.dict(by_alias=True, exclude={"id"})
    task_dict["created_at"] = datetime.now()
    task_dict["updated_at"] = datetime.now()
    result = await db.tasks.insert_one(task_dict)
    created = await db.tasks.find_one({"_id": result.inserted_id})
    return task_helper(created)

@app.get("/save-project-tasks", response_model=List[Task])
async def get_all_tasks(project_id: Optional[str] = None):
    query = {"project_id": project_id} if project_id else {}
    tasks = []
    cursor = db.tasks.find(query).sort("created_at", -1)
    async for task in cursor:
        tasks.append(task_helper(task))
    return tasks

@app.get("/save-project-tasks/{task_id}", response_model=Task)
async def get_task(task_id: str):
    if not ObjectId.is_valid(task_id):
        raise HTTPException(status_code=400, detail="Invalid ID")
    task = await db.tasks.find_one({"_id": ObjectId(task_id)})
    if not task:
        raise HTTPException(status_code=404, detail="Not found")
    return task_helper(task)

@app.put("/save-project-tasks/{task_id}", response_model=Task)
async def update_task(task_id: str, update: TaskUpdate):
    if not ObjectId.is_valid(task_id):
        raise HTTPException(status_code=400, detail="Invalid ID")
    data = {k: v for k, v in update.dict(exclude_unset=True).items() if v is not None}
    if data:
        data["updated_at"] = datetime.now()
        await db.tasks.update_one({"_id": ObjectId(task_id)}, {"$set": data})
    updated = await db.tasks.find_one({"_id": ObjectId(task_id)})
    if not updated:
        raise HTTPException(status_code=404, detail="Not found")
    return task_helper(updated)

@app.delete("/save-project-tasks/{task_id}", status_code=204)
async def delete_task(task_id: str):
    if not ObjectId.is_valid(task_id):
        raise HTTPException(status_code=400, detail="Invalid ID")
    result = await db.tasks.delete_one({"_id": ObjectId(task_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Not found")

@app.get("/save-project/{project_id}/stats")
async def get_project_stats(project_id: str):
    if not ObjectId.is_valid(project_id):
        raise HTTPException(status_code=400, detail="Invalid ID")
    tasks = []
    cursor = db.tasks.find({"project_id": project_id})
    async for task in cursor:
        tasks.append(task)
    return {
        "total_tasks": len(tasks),
        "pending": len([t for t in tasks if t.get("status") == "pending"]),
        "in_progress": len([t for t in tasks if t.get("status") == "in_progress"]),
        "completed": len([t for t in tasks if t.get("status") == "completed"]),
        "blocked": len([t for t in tasks if t.get("status") == "blocked"])
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
