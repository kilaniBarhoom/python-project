"""
Test MongoDB connection for tkinter app
Run this to verify your database connection works
"""
import sys
import os
from dotenv import load_dotenv

# Add parent directory to path
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, parent_dir)

# Load environment variables
env_path = os.path.join(parent_dir, '.env')
load_dotenv(env_path)

print("=" * 50)
print("MongoDB Connection Test")
print("=" * 50)
print()

# Check if MongoDB URI is loaded
mongo_uri = os.getenv('MONGODB_URI')
if not mongo_uri:
    print("✗ ERROR: MONGODB_URI not found in .env file")
    print(f"  Expected .env file at: {env_path}")
    sys.exit(1)

print("✓ MongoDB URI loaded from .env")
print()

# Try to connect to database
try:
    from models.database import Database

    print("Attempting to connect to MongoDB...")
    db = Database()

    # Test connection
    db_instance = db.get_database()

    # List collections to verify connection
    collections = db_instance.list_collection_names()

    print("✓ Successfully connected to MongoDB!")
    print()
    print(f"Database name: {db_instance.name}")
    print(f"Collections found: {len(collections)}")
    if collections:
        print(f"Collections: {', '.join(collections)}")
    print()
    print("=" * 50)
    print("✓ Connection test PASSED!")
    print("=" * 50)
    print()
    print("You can now run the tkinter app with:")
    print("  python main.py")

except Exception as e:
    print(f"✗ ERROR: Failed to connect to MongoDB")
    print(f"  Error: {str(e)}")
    print()
    print("Troubleshooting:")
    print("  1. Check that MongoDB URI is correct in .env file")
    print("  2. Verify network connection to MongoDB")
    print("  3. Ensure MongoDB instance is running")
    sys.exit(1)
