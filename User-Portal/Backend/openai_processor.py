"""
OpenAI Processor Module
Handles final response generation using OpenAI with API results
"""
from openai import OpenAI
from database import collection
from typing import Dict, Any
import json
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


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
    logger.info("=" * 80)
    logger.info(f"FINAL RESPONSE GENERATION STARTED - Agent: {agent_name}")
    logger.info(f"Timestamp: {datetime.now().isoformat()}")
    logger.info("-" * 80)
    
    # Get agent configuration
    agent = get_agent_by_name(agent_name)
    
    logger.info(f"User Query: {user_query}")
    logger.info(f"System Prompt: {agent['system_prompt'][:200]}...")
    
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

    api_results_str = json.dumps(api_results, indent=2, ensure_ascii=False)
    user_prompt = f"""User Query: {user_query}

API Results:
{api_results_str}

Please provide a clear answer to the user's query based on the API results above."""

    logger.info("-" * 80)
    logger.info("SYSTEM PROMPT SENT TO OpenAI:")
    logger.info(system_prompt[:500] + "..." if len(system_prompt) > 500 else system_prompt)
    logger.info("-" * 80)
    logger.info("USER PROMPT SENT TO OpenAI:")
    logger.info(f"User Query: {user_query}")
    logger.info(f"API Results Length: {len(api_results_str)} characters")
    if len(api_results_str) > 1000:
        logger.info("API Results (first 1000 chars):")
        logger.info(api_results_str[:1000] + "...")
    else:
        logger.info("API Results:")
        logger.info(api_results_str)
    logger.info("-" * 80)

    try:
        logger.info("Calling OpenAI API for final response generation...")
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        final_response = response.choices[0].message.content.strip()
        
        logger.info(f"OpenAI Response Received:")
        logger.info(f"  - Model: {response.model}")
        logger.info(f"  - Usage: {response.usage.total_tokens} tokens")
        logger.info(f"  - Prompt Tokens: {response.usage.prompt_tokens}")
        logger.info(f"  - Completion Tokens: {response.usage.completion_tokens}")
        logger.info("-" * 80)
        logger.info("FINAL RESPONSE GENERATED:")
        logger.info(final_response[:500] + "..." if len(final_response) > 500 else final_response)
        logger.info("=" * 80)
        
        return final_response
        
    except Exception as e:
        logger.error(f"Error generating final response: {str(e)}")
        raise Exception(f"Error generating final response: {str(e)}")



