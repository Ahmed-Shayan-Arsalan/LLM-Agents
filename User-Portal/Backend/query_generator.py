"""
Query Generator Module
Handles generation of API queries using OpenAI based on agent configuration
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


def generate_query(agent_name: str, user_query: str) -> Dict[str, Any]:
    """
    Generate an API query using OpenAI based on agent configuration and user query
    
    Args:
        agent_name: Name of the agent to use
        user_query: User's natural language query
        
    Returns:
        Generated query dictionary ready to be sent to the endpoint
    """
    # Get agent configuration
    agent = get_agent_by_name(agent_name)
    
    # Initialize OpenAI client with agent's API key
    client = OpenAI(api_key=agent["api_key"])
    
    # Build the prompt for query generation
    system_prompt = f"""You are a query generation assistant. Your job is to convert user queries into API query structures.

Agent Context:
- System Prompt: {agent['system_prompt']}
- Endpoint Info: {agent['endpoint_info']}
- Example Query: {json.dumps(agent['example_query'], indent=2)}
- Test Scenarios: {agent['test_scenarios']}

Your task:
1. Analyze the user's query
2. Generate an appropriate API query structure based on the example query format
3. Adapt the query parameters to match what the user is asking for
4. Return ONLY valid JSON that matches the example query structure
5. Do not include any explanations, comments, or markdown formatting - just the raw JSON

The query should be structured to retrieve data that will help answer the user's question."""

    user_prompt = f"""User Query: {user_query}

Generate an API query JSON structure based on the example query format. Return only the JSON, no other text."""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=1000
        )
        
        # Extract the generated query
        generated_text = response.choices[0].message.content.strip()
        
        # Remove markdown code blocks if present
        if generated_text.startswith("```json"):
            generated_text = generated_text[7:]
        if generated_text.startswith("```"):
            generated_text = generated_text[3:]
        if generated_text.endswith("```"):
            generated_text = generated_text[:-3]
        generated_text = generated_text.strip()
        
        # Parse JSON
        generated_query = json.loads(generated_text)
        
        return generated_query
        
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse generated query as JSON: {str(e)}")
    except Exception as e:
        raise Exception(f"Error generating query: {str(e)}")



