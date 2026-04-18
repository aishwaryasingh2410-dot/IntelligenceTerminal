import os
from dotenv import load_dotenv, find_dotenv
from pymongo import MongoClient, errors

# Load .env
load_dotenv(find_dotenv())

# Read URI
MONGO_URI = os.getenv("MONGO_URI")
print("MONGO_URI being used:", MONGO_URI)

# Try connecting
try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    db = client.get_default_database()
    print("Connected to database:", db.name)
    print("Collections:", db.list_collection_names())
except errors.ServerSelectionTimeoutError as e:
    print("Server selection timeout:", e)
except errors.OperationFailure as e:
    print("Authentication failed:", e)
except Exception as e:
    print("Other error:", e)
