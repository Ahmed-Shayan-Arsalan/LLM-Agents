"""
OpenAI Processor Module
Handles final response generation using OpenAI with API results
"""
from openai import OpenAI
from database import collection
from typing import Dict, Any
import json


def get_agent_by_name(agent_name: str) -> Dict[str, Any]:
    """Retrieve agent configuration from database"""
    agent = collection.find_one({"name": agent_name})
    if not agent:
        raise ValueError(f"Agent '{agent_name}' not found")
    return agent


def generate_final_response(agent_name: str, user_query: str, api_results: Dict[str, Any]) -> str:
    """
    Generate final response using OpenAI with API results
    
    Args:
        agent_name: Name of the agent
        user_query: Original user query
        api_results: Results from the API query
        
    Returns:
        Final response string
    """
    # Get agent configuration
    agent = get_agent_by_name(agent_name)
    
    # Initialize OpenAI client with agent's API key
    client = OpenAI(api_key=agent["api_key"])
    
    # Build the prompt for final response
    system_prompt = f"""You are a helpful assistant. {agent['system_prompt']}

Your task:
1. Analyze the API results provided
2. Answer the user's query based on the API data
3. Use the context from the endpoint information: {agent['endpoint_info']}
4. Provide a clear, helpful response that directly addresses the user's question
5. If the API results don't contain relevant information, say so clearly
6. Format your response in a way that's easy to understand"""

    user_prompt = f"""User Query: {user_query}

API Results:
{json.dumps(api_results, indent=2, ensure_ascii=False)}

Please provide a clear answer to the user's query based on the API results above."""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        raise Exception(f"Error generating final response: {str(e)}")



