from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from datetime import datetime, timezone
from bson import ObjectId
import os

from database import collection
from models import Agent, AgentCreate, AgentUpdate

app = FastAPI(
    title="LLM Agents Admin API",
    description="API for managing LLM agents",
    version="1.0.0"
)

# CORS configuration
cors_origins = os.environ.get("CORS_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def agent_helper(agent) -> dict:
    """Convert MongoDB document to dict with string _id"""
    if agent:
        agent["_id"] = str(agent["_id"])
        return agent
    return None


@app.get("/")
async def root():
    return {"message": "LLM Agents Admin API", "version": "1.0.0"}


@app.get("/api/agents", response_model=List[Agent], status_code=status.HTTP_200_OK)
async def get_all_agents():
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
async def get_agent(agent_id: str):
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
async def get_agent_by_name(agent_name: str):
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
async def create_agent(agent: AgentCreate):
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
async def update_agent(agent_id: str, agent_update: AgentUpdate):
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
async def delete_agent(agent_id: str):
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

