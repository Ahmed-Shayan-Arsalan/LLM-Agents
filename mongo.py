import os
from datetime import datetime, timezone

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

# Agent configuration - Simple and scalable structure
motie_checker = {
    "name": "MotieChecker",
    "api_key": os.environ.get("MOTIECHECKER_OPENAI_KEY", "sk-XXXXXXXXXXXXXXXXXXXXXXXXXXXX"),
    "system_prompt": (
            "You are a political analyst specializing in Dutch parliamentary voting behavior. "
            "Your job is to help young people understand how political parties vote on key issues "
            "like housing, climate, and education. Summarize votes in clear language, explain what "
            "they mean for young people, and list which parties voted for or against — without "
            "using technical jargon."
    ),
        "endpoint": "https://api.tweedekamer.nl/open_data",
    "endpoint_info": "Tweede Kamer Open Data API - Provides access to Dutch parliamentary voting data and motions",
    "example_query": {
            "type": "stemming",
            "query": {
                "bool": {
                    "must": [
                        {"match": {"omschrijving": "studenten"}},
                        {"range": {"datum": {"gte": "2023-01-01", "lte": "2023-12-31"}}},
                    ]
                }
            },
            "size": 1,
        },
    "test_scenarios": (
        "User prompt: 'What did parties vote on student housing last year?'\n\n"
        "Expected AI response:\n"
        "On November 16, 2023, a motion was submitted requesting extra funding for student housing.\n"
        "It was supported by parties like GroenLinks-PvdA, SP, Volt, and PvdD.\n"
        "VVD, PVV, NSC, and JA21 voted against it.\n"
        "This shows that left-leaning parties pushed for more housing support for students, "
        "while right-wing parties were more hesitant to allocate extra funds."
    ),
        "created_at": datetime.now(timezone.utc),
}

def upsert_agent(agent_data):
    """
    Insert or update an agent in the database.
    
    Args:
        agent_data: Dictionary containing agent information with required fields:
                   - name: String
                   - api_key: String
                   - system_prompt: String
                   - endpoint: String
                   - endpoint_info: String
                   - example_query: JSON (dict)
                   - test_scenarios: String
    
    Returns:
        Result object from MongoDB update_one operation
    """
result = collection.update_one(
        {"name": agent_data["name"]},
        {"$set": agent_data},
        upsert=True
)
    return result


def main():
    """Main function to set up agents in MongoDB."""
    try:
        # Test the connection first
        client.admin.command("ping")
        print("Successfully connected to MongoDB!")
        
        # Upsert MotieChecker agent
        result = upsert_agent(motie_checker)

if result.upserted_id:
            print(f"✓ Inserted new agent '{motie_checker['name']}' with _id={result.upserted_id}")
else:
            print(f"✓ Updated existing agent '{motie_checker['name']}'")
            
        # Add more agents here as needed
        # Example:
        # another_agent = {
        #     "name": "AnotherAgent",
        #     "api_key": "...",
        #     "system_prompt": "...",
        #     "endpoint": "...",
        #     "endpoint_info": "...",
        #     "example_query": {...},
        #     "test_scenarios": "...",
        #     "created_at": datetime.now(timezone.utc),
        # }
        # upsert_agent(another_agent)
        
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        raise
    finally:
        client.close()


if __name__ == "__main__":
    main()
