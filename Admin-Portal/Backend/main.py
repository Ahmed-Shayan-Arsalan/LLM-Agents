from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Optional
from datetime import datetime, timezone
from bson import ObjectId
import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic import BaseModel

# Load environment variables from .env file in the same directory as this script
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

from database import collection
from models import Agent, AgentCreate, AgentUpdate

app = FastAPI(
    title="LLM Agents Admin API",
    description="API for managing LLM agents",
    version="1.0.0"
)

# CORS configuration
# Get CORS origins from environment variable, default includes localhost and production frontend
cors_origins_env = os.environ.get("CORS_ORIGINS", "")
if cors_origins_env:
    cors_origins = cors_origins_env.split(",")
else:
    # Default origins: localhost for development and production frontend
    cors_origins = [
        "http://localhost:3000",
        "https://llm-agents-admin-frontend.vercel.app",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_origin_regex=r"https://llm-agents-admin-frontend-.*\.vercel\.app",  # Allow preview deployments
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Password authentication
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")
if not ADMIN_PASSWORD:
    raise ValueError("ADMIN_PASSWORD environment variable is required. Please set it in .env file.")
security = HTTPBearer()

# Authentication models
class LoginRequest(BaseModel):
    password: str

class LoginResponse(BaseModel):
    success: bool
    message: str
    token: Optional[str] = None

# Simple token (in production, use JWT)
VALID_TOKEN = "admin_authenticated_token"

def verify_password(password: str) -> bool:
    """Verify the admin password"""
    return password == ADMIN_PASSWORD

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> bool:
    """Verify the authentication token"""
    return credentials.credentials == VALID_TOKEN


def agent_helper(agent) -> dict:
    """Convert MongoDB document to dict with string _id"""
    if agent:
        agent["_id"] = str(agent["_id"])
        return agent
    return None


@app.get("/")
async def root():
    return {"message": "LLM Agents Admin API", "version": "1.0.0"}

@app.post("/api/auth/login", response_model=LoginResponse)
async def login(login_request: LoginRequest):
    """Login endpoint to authenticate admin"""
    if verify_password(login_request.password):
        return LoginResponse(
            success=True,
            message="Authentication successful",
            token=VALID_TOKEN
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password"
        )

@app.get("/api/auth/verify")
async def verify_auth(is_authenticated: bool = Depends(verify_token)):
    """Verify if user is authenticated"""
    return {"authenticated": True}


@app.get("/api/agents", response_model=List[Agent], status_code=status.HTTP_200_OK)
async def get_all_agents(is_authenticated: bool = Depends(verify_token)):
    """Get all agents from the database"""
    try:
        agents = []
        for agent in collection.find():
            agents.append(agent_helper(agent))
        return agents
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching agents: {str(e)}"
        )


@app.get("/api/agents/{agent_id}", response_model=Agent, status_code=status.HTTP_200_OK)
async def get_agent(agent_id: str, is_authenticated: bool = Depends(verify_token)):
    """Get a single agent by ID"""
    try:
        if not ObjectId.is_valid(agent_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid agent ID format"
            )
        
        agent = collection.find_one({"_id": ObjectId(agent_id)})
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent with ID {agent_id} not found"
            )
        
        return agent_helper(agent)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching agent: {str(e)}"
        )


@app.get("/api/agents/name/{agent_name}", response_model=Agent, status_code=status.HTTP_200_OK)
async def get_agent_by_name(agent_name: str, is_authenticated: bool = Depends(verify_token)):
    """Get a single agent by name"""
    try:
        agent = collection.find_one({"name": agent_name})
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent with name '{agent_name}' not found"
            )
        
        return agent_helper(agent)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching agent: {str(e)}"
        )


@app.post("/api/agents", response_model=Agent, status_code=status.HTTP_201_CREATED)
async def create_agent(agent: AgentCreate, is_authenticated: bool = Depends(verify_token)):
    """Create a new agent"""
    try:
        # Check if agent with same name already exists
        existing = collection.find_one({"name": agent.name})
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Agent with name '{agent.name}' already exists"
            )
        
        # Prepare agent data
        agent_dict = agent.model_dump()
        agent_dict["created_at"] = datetime.now(timezone.utc)
        
        # Insert agent
        result = collection.insert_one(agent_dict)
        
        # Fetch and return the created agent
        created_agent = collection.find_one({"_id": result.inserted_id})
        return agent_helper(created_agent)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating agent: {str(e)}"
        )


@app.put("/api/agents/{agent_id}", response_model=Agent, status_code=status.HTTP_200_OK)
async def update_agent(agent_id: str, agent_update: AgentUpdate, is_authenticated: bool = Depends(verify_token)):
    """Update an existing agent"""
    try:
        if not ObjectId.is_valid(agent_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid agent ID format"
            )
        
        # Check if agent exists
        existing = collection.find_one({"_id": ObjectId(agent_id)})
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent with ID {agent_id} not found"
            )
        
        # Prepare update data (only include fields that are provided)
        update_data = {k: v for k, v in agent_update.model_dump().items() if v is not None}
        
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update"
            )
        
        # If name is being updated, check for conflicts
        if "name" in update_data and update_data["name"] != existing["name"]:
            name_conflict = collection.find_one({"name": update_data["name"]})
            if name_conflict:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Agent with name '{update_data['name']}' already exists"
                )
        
        # Update agent
        collection.update_one(
            {"_id": ObjectId(agent_id)},
            {"$set": update_data}
        )
        
        # Fetch and return updated agent
        updated_agent = collection.find_one({"_id": ObjectId(agent_id)})
        return agent_helper(updated_agent)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating agent: {str(e)}"
        )


@app.delete("/api/agents/{agent_id}", status_code=status.HTTP_200_OK)
async def delete_agent(agent_id: str, is_authenticated: bool = Depends(verify_token)):
    """Delete an agent"""
    try:
        if not ObjectId.is_valid(agent_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid agent ID format"
            )
        
        # Check if agent exists
        existing = collection.find_one({"_id": ObjectId(agent_id)})
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent with ID {agent_id} not found"
            )
        
        # Delete agent
        result = collection.delete_one({"_id": ObjectId(agent_id)})
        
        if result.deleted_count == 1:
            return {"message": f"Agent with ID {agent_id} deleted successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete agent"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting agent: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("BACKEND_PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

