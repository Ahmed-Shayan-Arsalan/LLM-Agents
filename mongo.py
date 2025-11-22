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
    "api_key": os.environ.get("MOTIECHECKER_OPENAI_KEY", ""),
    "system_prompt": (
            "You are a political analyst specializing in Dutch parliamentary voting behavior. "
            "Your job is to help young people understand how political parties vote on key issues "
            "like housing, climate, and education. Summarize votes in clear language, explain what "
            "they mean for young people, and list which parties voted for or against — without "
            "using technical jargon."
    ),
    "endpoint": "https://gegevensmagazijn.tweedekamer.nl/OData/v4/2.0/",
    "endpoint_info": "Tweede Kamer OData API - Provides access to Dutch parliamentary voting data (Stemming) and decisions (Besluit). Use Besluit entity for text searches via BesluitTekst field.",
    "example_query": {
        "entity_set": "Besluit",
        "filter": "contains(BesluitTekst,'studenten') and ApiGewijzigdOp ge 2019-01-01T00:00:00Z and ApiGewijzigdOp le 2019-12-31T23:59:59Z",
        "top": 10,
        "select": "Id,BesluitTekst,ApiGewijzigdOp,BesluitSoort"
    },
    "test_scenarios": (
        "User prompt: 'What did parties vote on student housing in 2019?'\n\n"
        "Expected AI response:\n"
        "In 2019, the Dutch Parliament discussed several motions and decisions related to student housing. "
        "For example, there were discussions about allocating more funding for student housing and addressing "
        "the shortage of affordable housing for students. The votes typically showed left-leaning parties "
        "(like GroenLinks, PvdA, SP) supporting more government intervention and funding, while right-wing "
        "parties (like VVD, CDA) were more cautious about increasing public spending.\n\n"
        "Note: Search for 'studenten' or 'studentenhuisvesting' in BesluitTekst field. "
        "Use ApiGewijzigdOp for date filtering (not Datum). "
        "Available fields in Besluit: Id, BesluitTekst, ApiGewijzigdOp, BesluitSoort, Status, Opmerking."
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
            print(f"[+] Inserted new agent '{motie_checker['name']}' with _id={result.upserted_id}")
        else:
            print(f"[+] Updated existing agent '{motie_checker['name']}'")
            
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
