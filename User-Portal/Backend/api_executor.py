"""
API Executor Module
Handles execution of queries against external APIs
"""
import httpx
from typing import Dict, Any
from database import collection


def get_agent_by_name(agent_name: str) -> Dict[str, Any]:
    """Retrieve agent configuration from database"""
    agent = collection.find_one({"name": agent_name})
    if not agent:
        raise ValueError(f"Agent '{agent_name}' not found")
    return agent


async def execute_query(agent_name: str, query: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute a query against the agent's endpoint
    
    Args:
        agent_name: Name of the agent
        query: Query dictionary to send to the endpoint
        
    Returns:
        API response data
    """
    # Get agent configuration
    agent = get_agent_by_name(agent_name)
    endpoint = agent["endpoint"]
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                endpoint,
                json=query,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                }
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        raise Exception(f"API request failed with status {e.response.status_code}: {e.response.text}")
    except httpx.TimeoutException:
        raise Exception("API request timed out")
    except Exception as e:
        raise Exception(f"Error executing API query: {str(e)}")



