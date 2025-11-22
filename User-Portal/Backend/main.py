"""
User Portal Backend API
Handles user interactions with agents
"""
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from bson import ObjectId
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from database import collection
from models import QueryGenerationRequest, QueryGenerationResponse, OpenAIRequest, OpenAIResponse
from query_generator import generate_query
from api_executor import execute_query
from openai_processor import generate_final_response

app = FastAPI(
    title="LLM Agents User Portal API",
    description="API for users to interact with LLM agents",
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
        "http://localhost:3001",
        "https://llm-agents-user-frontend.vercel.app",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_origin_regex=r"https://llm-agents-user-frontend-.*\.vercel\.app",  # Allow preview deployments
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
    return {"message": "LLM Agents User Portal API", "version": "1.0.0"}


@app.get("/api/agents", status_code=status.HTTP_200_OK)
async def get_all_agents():
    """Get all available agents"""
    try:
        agents = []
        for agent in collection.find():
            # Only return necessary fields for user selection
            agent_dict = agent_helper(agent)
            if agent_dict:
                agents.append({
                    "_id": agent_dict["_id"],
                    "name": agent_dict["name"],
                    "endpoint_info": agent_dict.get("endpoint_info", ""),
                })
        return agents
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching agents: {str(e)}"
        )


@app.get("/api/agents/{agent_name}", status_code=status.HTTP_200_OK)
async def get_agent_by_name(agent_name: str):
    """Get agent details by name"""
    try:
        agent = collection.find_one({"name": agent_name})
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent '{agent_name}' not found"
            )
        
        # Return only necessary fields
        agent_dict = agent_helper(agent)
        return {
            "_id": agent_dict["_id"],
            "name": agent_dict["name"],
            "endpoint_info": agent_dict.get("endpoint_info", ""),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching agent: {str(e)}"
        )


@app.post("/api/generate-query", response_model=QueryGenerationResponse, status_code=status.HTTP_200_OK)
async def generate_query_endpoint(request: QueryGenerationRequest):
    """
    Generate an API query based on user query and agent configuration
    """
    try:
        generated_query = generate_query(request.agent_name, request.user_query)
        return QueryGenerationResponse(
            generated_query=generated_query,
            success=True,
            message="Query generated successfully"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating query: {str(e)}"
        )


@app.post("/api/get-response", response_model=OpenAIResponse, status_code=status.HTTP_200_OK)
async def get_openai_response(request: OpenAIRequest):
    """
    Get final OpenAI response using user query and API results
    """
    try:
        response = generate_final_response(
            request.agent_name,
            request.user_query,
            request.api_results
        )
        return OpenAIResponse(
            response=response,
            success=True,
            message="Response generated successfully"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating response: {str(e)}"
        )


@app.post("/api/complete-query", status_code=status.HTTP_200_OK)
async def complete_query(request: QueryGenerationRequest):
    """
    Complete workflow: Generate query -> Execute API -> Get OpenAI response
    This is a convenience endpoint that combines all steps
    """
    import logging
    from datetime import datetime
    
    logger = logging.getLogger(__name__)
    
    logger.info("=" * 80)
    logger.info("=" * 80)
    logger.info(f"COMPLETE QUERY WORKFLOW STARTED")
    logger.info(f"Agent: {request.agent_name}")
    logger.info(f"User Query: {request.user_query}")
    logger.info(f"Timestamp: {datetime.now().isoformat()}")
    logger.info("=" * 80)
    logger.info("=" * 80)
    
    try:
        # Step 1: Generate query
        logger.info("\n>>> STEP 1: QUERY GENERATION <<<\n")
        generated_query = generate_query(request.agent_name, request.user_query)
        
        # Step 2: Execute API query
        logger.info("\n>>> STEP 2: API EXECUTION <<<\n")
        api_results = await execute_query(request.agent_name, generated_query)
        
        # Step 3: Generate final response
        logger.info("\n>>> STEP 3: FINAL RESPONSE GENERATION <<<\n")
        final_response = generate_final_response(
            request.agent_name,
            request.user_query,
            api_results
        )
        
        logger.info("=" * 80)
        logger.info("=" * 80)
        logger.info("WORKFLOW COMPLETED SUCCESSFULLY")
        logger.info("=" * 80)
        logger.info("=" * 80)
        
        return {
            "response": final_response,
            "generated_query": generated_query,
            "api_results": api_results,
            "success": True
        }
    except ValueError as e:
        logger.error(f"ValueError: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Exception in complete_query: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing query: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("BACKEND_PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

