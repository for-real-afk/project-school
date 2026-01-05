import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"

def print_response(title, response):
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    if response.status_code != 204:
        print(f"Response: {json.dumps(response.json(), indent=2, default=str)}")
    print()

def main():
    print("Testing Project Management API with MongoDB")
    print("="*60)
    
    # Test 1: Health check
    print("\n1. Health Check...")
    response = requests.get(f"{BASE_URL}/health")
    print_response("HEALTH CHECK", response)
    
    # Test 2: Create a project
    print("\n2. Creating a new project...")
    project_data = {
        "name": "Alumnx AI Training Platform",
        "description": "Full Stack AI Engineer Program Development",
        "status": "active",
        "start_date": datetime.now().isoformat(),
        "end_date": (datetime.now() + timedelta(days=90)).isoformat()
    }
    
    response = requests.post(f"{BASE_URL}/save-project", json=project_data)
    print_response("CREATE PROJECT", response)
    project = response.json()
    project_id = project["id"]
    
    # Test 3: Create tasks
    print("\n3. Creating tasks for the project...")
    tasks_data = [
        {
            "project_id": project_id,
            "title": "Setup RAG System Infrastructure",
            "description": "Setup vector database and embedding models",
            "status": "completed",
            "priority": "high",
            "assigned_to": "vijender@alumnxai.com",
            "due_date": (datetime.now() + timedelta(days=7)).isoformat()
        },
        {
            "project_id": project_id,
            "title": "Develop AI Agents Module",
            "description": "Build autonomous AI agents with LangChain",
            "status": "in_progress",
            "priority": "high",
            "assigned_to": "team@alumnxai.com",
            "due_date": (datetime.now() + timedelta(days=14)).isoformat()
        },
        {
            "project_id": project_id,
            "title": "Create LLM Fine-tuning Workshop",
            "description": "Hands-on workshop for model fine-tuning",
            "status": "pending",
            "priority": "medium",
            "assigned_to": "vijender@alumnxai.com",
            "due_date": (datetime.now() + timedelta(days=21)).isoformat()
        },
        {
            "project_id": project_id,
            "title": "Build Assessment Platform",
            "description": "MCQ and coding assessment system",
            "status": "pending",
            "priority": "urgent",
            "due_date": (datetime.now() + timedelta(days=28)).isoformat()
        }
    ]
    
    task_ids = []
    for task_data in tasks_data:
        response = requests.post(f"{BASE_URL}/save-project-tasks", json=task_data)
        print_response(f"CREATE TASK: {task_data['title']}", response)
        task_ids.append(response.json()["id"])
    
    # Test 4: Get all projects
    print("\n4. Getting all projects...")
    response = requests.get(f"{BASE_URL}/save-project")
    print_response("GET ALL PROJECTS", response)
    
    # Test 5: Get specific project
    print("\n5. Getting specific project...")
    response = requests.get(f"{BASE_URL}/save-project/{project_id}")
    print_response("GET PROJECT BY ID", response)
    
    # Test 6: Get all tasks for project
    print("\n6. Getting all tasks for the project...")
    response = requests.get(f"{BASE_URL}/save-project-tasks?project_id={project_id}")
    print_response("GET TASKS BY PROJECT", response)
    
    # Test 7: Update a task
    print("\n7. Updating task status...")
    update_data = {
        "status": "completed",
        "description": "AI Agents module completed with practical examples"
    }
    response = requests.put(f"{BASE_URL}/save-project-tasks/{task_ids[1]}", json=update_data)
    print_response("UPDATE TASK", response)
    
    # Test 8: Get project statistics
    print("\n8. Getting project statistics...")
    response = requests.get(f"{BASE_URL}/save-project/{project_id}/stats")
    print_response("PROJECT STATISTICS", response)
    
    # Test 9: Update project
    print("\n9. Updating project...")
    project_update = {
        "description": "Full Stack AI Engineer Program - Phase 1 in progress",
        "status": "active"
    }
    response = requests.put(f"{BASE_URL}/save-project/{project_id}", json=project_update)
    print_response("UPDATE PROJECT", response)
    
    # Test 10: Get specific task
    print("\n10. Getting specific task...")
    response = requests.get(f"{BASE_URL}/save-project-tasks/{task_ids[0]}")
    print_response("GET TASK BY ID", response)
    
    print("\n" + "="*60)
    print("All tests completed successfully!")
    print("="*60)
    print(f"\nProject ID: {project_id}")
    print(f"Task IDs: {task_ids}")
    print(f"\nView in MongoDB:")
    print(f"db.projects.findOne({{_id: ObjectId('{project_id}')}})")

if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to the API server.")
        print("Please make sure:")
        print("1. MongoDB is running")
        print("2. .env file is configured with MONGODB_URL")
        print("3. FastAPI server is running: python main.py")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
