# Project Management API with MongoDB

A production-ready FastAPI application with MongoDB for managing projects and tasks with full CRUD operations.

## Features

- ✅ Complete CRUD operations for Projects and Tasks
- ✅ MongoDB integration with Motor (async driver)
- ✅ Environment variable configuration
- ✅ Automatic database indexing for performance
- ✅ Project-Task relationship management
- ✅ Project statistics endpoint
- ✅ Input validation with Pydantic
- ✅ Auto-generated API documentation
- ✅ CORS enabled for frontend integration

## Prerequisites

- Python 3.8 or higher
- MongoDB (local installation or MongoDB Atlas account)
- pip (Python package manager)

## Installation

### 1. Clone/Create Project Directory

```bash
mkdir project-management-api
cd project-management-api
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure MongoDB Connection

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` and add your MongoDB connection string:

**For Local MongoDB:**
```env
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=project_management
```

**For MongoDB Atlas:**
```env
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
DATABASE_NAME=project_management
```

### 5. Start MongoDB (if using local)

```bash
# On macOS with Homebrew
brew services start mongodb-community

# On Ubuntu/Linux
sudo systemctl start mongod

# On Windows
net start MongoDB
```

## Running the Application

```bash
python main.py
```

Or using uvicorn directly:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: `http://localhost:8000`

## API Documentation

Interactive API documentation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## MongoDB Collections

The application automatically creates two collections:
- `projects` - Stores project documents
- `tasks` - Stores task documents with project_id references

Indexes are automatically created on:
- `projects.name`
- `projects.status`
- `tasks.project_id`
- `tasks.status`
- `tasks.priority`

## API Endpoints

### Projects

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/save-project` | Create a new project |
| GET | `/save-project` | Get all projects |
| GET | `/save-project/{project_id}` | Get a specific project |
| PUT | `/save-project/{project_id}` | Update a project |
| DELETE | `/save-project/{project_id}` | Delete a project |
| GET | `/save-project/{project_id}/stats` | Get project statistics |

### Tasks

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/save-project-tasks` | Create a new task |
| GET | `/save-project-tasks` | Get all tasks (optional project_id filter) |
| GET | `/save-project-tasks/{task_id}` | Get a specific task |
| PUT | `/save-project-tasks/{task_id}` | Update a task |
| DELETE | `/save-project-tasks/{task_id}` | Delete a task |

## Usage Examples

### 1. Create a Project

```bash
curl -X POST "http://localhost:8000/save-project" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "AI Training Platform",
    "description": "Full Stack AI Engineer Program",
    "status": "active",
    "start_date": "2025-01-10T00:00:00",
    "end_date": "2025-03-31T00:00:00"
  }'
```

**Response:**
```json
{
  "id": "677b2c8d1234567890abcdef",
  "name": "AI Training Platform",
  "description": "Full Stack AI Engineer Program",
  "status": "active",
  "start_date": "2025-01-10T00:00:00",
  "end_date": "2025-03-31T00:00:00",
  "created_at": "2025-01-06T10:30:00",
  "updated_at": "2025-01-06T10:30:00"
}
```

### 2. Create a Task

```bash
curl -X POST "http://localhost:8000/save-project-tasks" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "677b2c8d1234567890abcdef",
    "title": "Develop RAG System Module",
    "description": "Create comprehensive content on RAG systems",
    "status": "in_progress",
    "priority": "high",
    "assigned_to": "vijender@alumnxai.com",
    "due_date": "2025-01-20T00:00:00"
  }'
```

### 3. Get All Projects

```bash
curl -X GET "http://localhost:8000/save-project"
```

### 4. Get Tasks for a Project

```bash
curl -X GET "http://localhost:8000/save-project-tasks?project_id=677b2c8d1234567890abcdef"
```

### 5. Update a Task

```bash
curl -X PUT "http://localhost:8000/save-project-tasks/677b2c9d1234567890abcdef" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "completed",
    "description": "RAG system module completed with examples"
  }'
```

### 6. Get Project Statistics

```bash
curl -X GET "http://localhost:8000/save-project/677b2c8d1234567890abcdef/stats"
```

**Response:**
```json
{
  "total_tasks": 5,
  "pending": 2,
  "in_progress": 2,
  "completed": 1,
  "blocked": 0
}
```

## Data Models

### Project Schema
```json
{
  "id": "ObjectId (auto-generated)",
  "name": "string (required, 1-200 chars)",
  "description": "string (optional)",
  "status": "active|completed|on_hold|cancelled (default: active)",
  "start_date": "datetime (optional)",
  "end_date": "datetime (optional)",
  "created_at": "datetime (auto)",
  "updated_at": "datetime (auto)"
}
```

### Task Schema
```json
{
  "id": "ObjectId (auto-generated)",
  "project_id": "string (required, must be valid project ID)",
  "title": "string (required, 1-200 chars)",
  "description": "string (optional)",
  "status": "pending|in_progress|completed|blocked (default: pending)",
  "priority": "low|medium|high|urgent (default: medium)",
  "assigned_to": "string (optional)",
  "due_date": "datetime (optional)",
  "created_at": "datetime (auto)",
  "updated_at": "datetime (auto)"
}
```

## Testing with Python

Create a test file `test_mongodb.py`:

```python
import requests
import json

BASE_URL = "http://localhost:8000"

# Create project
project = {
    "name": "Full Stack AI Engineer Course",
    "description": "Alumnx AI Labs training program",
    "status": "active"
}

response = requests.post(f"{BASE_URL}/save-project", json=project)
project_result = response.json()
project_id = project_result["id"]
print(f"Created Project: {project_id}")

# Create task
task = {
    "project_id": project_id,
    "title": "RAG System Development",
    "status": "in_progress",
    "priority": "high"
}

response = requests.post(f"{BASE_URL}/save-project-tasks", json=task)
task_result = response.json()
print(f"Created Task: {task_result['id']}")

# Get statistics
response = requests.get(f"{BASE_URL}/save-project/{project_id}/stats")
print("Stats:", response.json())
```

## MongoDB Atlas Setup (Cloud Database)

1. **Create Account**: Sign up at https://www.mongodb.com/cloud/atlas
2. **Create Cluster**: Choose free tier (M0)
3. **Create Database User**: Set username and password
4. **Whitelist IP**: Add your IP or use 0.0.0.0/0 for testing
5. **Get Connection String**: Copy from "Connect" button
6. **Update .env**: Paste connection string in MONGODB_URL

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| MONGODB_URL | MongoDB connection string | mongodb://localhost:27017 |
| DATABASE_NAME | Database name | project_management |

## Error Handling

The API returns appropriate HTTP status codes:
- `200` - Success
- `201` - Created
- `204` - No Content (successful deletion)
- `400` - Bad Request (invalid input)
- `404` - Not Found
- `500` - Internal Server Error
- `503` - Service Unavailable (database connection issue)

## Performance Tips

1. **Indexing**: Indexes are automatically created on frequently queried fields
2. **Pagination**: Use `skip` and `limit` parameters for large datasets
3. **Connection Pooling**: Motor handles connection pooling automatically
4. **Async Operations**: All database operations are asynchronous for better performance

## Troubleshooting

**Connection Error:**
```
Error connecting to MongoDB: [Errno 61] Connection refused
```
- Check if MongoDB is running
- Verify connection string in .env file
- Check firewall settings

**Invalid ObjectId:**
```
Invalid project ID format
```
- Ensure you're using MongoDB ObjectId format (24 hex characters)
- Don't use UUIDs from previous version

**Authentication Failed:**
```
Authentication failed
```
- Verify username/password in connection string
- Check database user permissions in MongoDB Atlas

## Future Enhancements

- [ ] User authentication with JWT
- [ ] Role-based access control
- [ ] Task comments and attachments
- [ ] Email notifications
- [ ] Advanced search and filtering
- [ ] Real-time updates with WebSockets
- [ ] Data export (CSV, Excel)
- [ ] Task dependencies and subtasks

## License

MIT License
