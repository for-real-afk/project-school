"""
MongoDB Connection Test Script
This script tests the connection to your MongoDB Atlas database
"""

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get the connection string from .env
uri = os.getenv("MONGODB_URL")
database_name = os.getenv("DATABASE_NAME", "projects")

print("Testing MongoDB Connection...")
print(f"Database: {database_name}")
print("-" * 60)

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

try:
    # Test the connection
    client.admin.command('ping')
    print("✅ Successfully connected to MongoDB Atlas!")
    
    # Get database
    db = client[database_name]
    
    # List existing collections
    collections = db.list_collection_names()
    print(f"\n📁 Existing collections in '{database_name}' database:")
    if collections:
        for collection in collections:
            count = db[collection].count_documents({})
            print(f"   - {collection} ({count} documents)")
    else:
        print("   (No collections yet - they will be created automatically)")
    
    # Show what collections will be created
    print(f"\n🔧 This API will use the following collections:")
    print(f"   - projects (for storing project documents)")
    print(f"   - tasks (for storing task documents)")
    
    print("\n✅ Connection test successful!")
    print("\nYou can now run: python main.py")
    
except Exception as e:
    print(f"\n❌ Connection failed!")
    print(f"Error: {e}")
    print("\nTroubleshooting:")
    print("1. Make sure you've replaced <db_password> in .env file")
    print("2. Check your MongoDB Atlas whitelist settings")
    print("3. Verify your database user credentials")
    
finally:
    client.close()
