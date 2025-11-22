import os
from pymongo import MongoClient
from pymongo.server_api import ServerApi

# MongoDB connection configuration
MONGO_USER = os.environ.get("MONGO_USER", "TrueAdmin")
MONGO_PASS = os.environ.get("MONGO_PASS", "TruePassword")
MONGO_APP = os.environ.get("MONGO_APPNAME", "Chatapi")
MONGO_HOST = os.environ.get("MONGO_HOST", "chatapi.yzflq8h.mongodb.net")

uri = f"mongodb+srv://{MONGO_USER}:{MONGO_PASS}@{MONGO_HOST}/?appName={MONGO_APP}&retryWrites=true&w=majority"

client = MongoClient(
    uri,
    server_api=ServerApi("1"),
    tls=True,
    tlsAllowInvalidCertificates=False,
    connectTimeoutMS=30000,
    serverSelectionTimeoutMS=30000,
)

db = client["LLM_Agents"]
collection = db["Agent_info"]



