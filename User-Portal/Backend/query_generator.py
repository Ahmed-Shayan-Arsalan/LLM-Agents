"""
Query Generator Module
Handles generation of API queries using OpenAI based on agent configuration
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


def generate_query(agent_name: str, user_query: str) -> Dict[str, Any]:
    """
    Generate an API query using OpenAI based on agent configuration and user query
    
    Args:
        agent_name: Name of the agent to use
        user_query: User's natural language query
        
    Returns:
        Generated query dictionary ready to be sent to the endpoint
    """
    logger.info("=" * 80)
    logger.info(f"QUERY GENERATION STARTED - Agent: {agent_name}")
    logger.info(f"Timestamp: {datetime.now().isoformat()}")
    logger.info("-" * 80)
    
    # Get agent configuration
    agent = get_agent_by_name(agent_name)
    endpoint = agent['endpoint']
    example_query = agent.get('example_query', {})
    
    logger.info(f"Agent Configuration Retrieved:")
    logger.info(f"  - Endpoint: {endpoint}")
    logger.info(f"  - System Prompt: {agent['system_prompt'][:100]}...")
    
    # Detect query structure from example query
    has_odata_structure = "entity_set" in example_query or "filter" in example_query
    has_elasticsearch_structure = "query" in example_query and isinstance(example_query.get("query"), dict)
    
    # Check if endpoint is OData
    is_odata = "/OData/" in endpoint or endpoint.endswith("/OData/v4/2.0") or endpoint.endswith("/OData/v4/2.0/")
    
    # Initialize OpenAI client with agent's API key
    client = OpenAI(api_key=agent["api_key"])
    
    # Build API-specific context based on endpoint type
    api_context = ""
    if is_odata:
        api_context = """
IMPORTANT: This is an OData API endpoint.

OData Query Structure:
- OData queries use entity sets (like database tables) accessed via GET requests
- Query parameters use $ prefix: $filter, $top, $select, $orderby, $expand
- Entity set names are usually case-sensitive

Common OData Query Format:
{
  "entity_set": "EntityName",
  "filter": "FieldName eq 'value' or contains(TextField,'keyword')",
  "top": 10,
  "select": "Field1,Field2,Field3"
}

OData $filter Operators:
- Logical: and, or, not
- Comparison: eq (equal), ne (not equal), gt (greater), ge (greater or equal), lt (less), le (less or equal)
- String functions: contains(field,'text'), startswith(field,'text'), endswith(field,'text')
- Date comparison: use ISO 8601 format (e.g., 2023-01-01T00:00:00Z)
- Example: FieldName ge 2023-01-01T00:00:00Z and FieldName le 2023-12-31T23:59:59Z

CRITICAL INSTRUCTIONS FOR OData:
1. Use ONLY the field names shown in the example query - do NOT invent field names
2. Entity set names from the example query are the correct ones to use
3. Date/time fields should use ISO 8601 format with timezone (e.g., 2023-01-01T00:00:00Z)
4. String values in filters use single quotes: 'value'
5. Field names in OData are case-sensitive - match the example query exactly
6. If the example query shows specific field names for dates or descriptions, use those exact names
"""
    elif has_elasticsearch_structure:
        api_context = """
IMPORTANT: This is an Elasticsearch-style API endpoint.

Elasticsearch Query Structure:
- Uses POST requests with JSON body
- Query structure typically includes: query, size, from, sort
- Supports complex boolean queries with must, should, must_not

Common Elasticsearch Query Format:
{
  "query": {
    "bool": {
      "must": [
        {"match": {"field": "value"}},
        {"range": {"date_field": {"gte": "2023-01-01", "lte": "2023-12-31"}}}
      ]
    }
  },
  "size": 10
}

CRITICAL INSTRUCTIONS FOR Elasticsearch:
1. Use ONLY the field names and query structure shown in the example query
2. Match the nesting structure of the example query exactly
3. Date formats should match the example query format
"""
    else:
        api_context = """
IMPORTANT: This is a REST API endpoint.

REST API Query Structure:
- The example query shows the EXACT structure this API expects
- Some APIs use POST with JSON body, others use GET with URL parameters
- Field names, nesting, and data types must match the example query

CRITICAL INSTRUCTIONS:
1. Use ONLY the field names shown in the example query
2. Match the structure and nesting of the example query EXACTLY
3. Adapt only the values to match what the user is asking for
4. Do not add or remove fields unless the user explicitly requests data not covered by the example
"""
    
    # Build the prompt for query generation - adapt based on example query structure
    system_prompt = f"""You are a query generation assistant. Your job is to convert user queries into API query structures.

Agent Context:
- System Prompt: {agent['system_prompt']}
- Endpoint Info: {agent['endpoint_info']}
- Endpoint URL: {endpoint}
- Example Query: {json.dumps(example_query, indent=2)}
- Test Scenarios: {agent['test_scenarios']}
{api_context}
CRITICAL INSTRUCTIONS:
1. The example query is your PRIMARY reference - it shows the EXACT format, field names, and structure this API expects
2. Analyze the example query structure carefully and match it EXACTLY
3. Use ONLY field names that appear in the example query - never invent or guess field names
4. Maintain the same JSON structure, nesting, and data types as the example
5. Adapt ONLY the values to match what the user is asking for
6. Return ONLY valid JSON that matches the example query format
7. Do not include any explanations, comments, or markdown formatting - just the raw JSON

Your task:
1. Study the example query structure - this is your template
2. Identify what the user is asking for
3. Map the user's request to the fields and structure shown in the example query
4. Generate a query that uses the SAME field names and structure as the example
5. If a field exists in the example for dates, use that field for date filtering
6. If a field exists in the example for text search, use that field for text matching
7. If the user asks for something not covered by the example query fields, do your best to adapt the closest matching field

The query should retrieve data that helps answer the user's question while strictly following the example query format."""

    user_prompt = f"""User Query: {user_query}

Generate an API query JSON structure based on the example query format. Return only the JSON, no other text."""

    logger.info(f"User Query: {user_query}")
    logger.info("-" * 80)
    logger.info("SYSTEM PROMPT SENT TO OpenAI:")
    logger.info(system_prompt[:500] + "..." if len(system_prompt) > 500 else system_prompt)
    logger.info("-" * 80)
    logger.info("USER PROMPT SENT TO OpenAI:")
    logger.info(user_prompt)
    logger.info("-" * 80)

    try:
        logger.info("Calling OpenAI API for query generation...")
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=1000
        )
        
        logger.info(f"OpenAI Response Received:")
        logger.info(f"  - Model: {response.model}")
        logger.info(f"  - Usage: {response.usage.total_tokens} tokens")
        
        # Extract the generated query
        generated_text = response.choices[0].message.content.strip()
        logger.info("Raw Generated Text:")
        logger.info(generated_text[:500] + "..." if len(generated_text) > 500 else generated_text)
        
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
        
        logger.info("-" * 80)
        logger.info("GENERATED QUERY (Parsed JSON):")
        logger.info(json.dumps(generated_query, indent=2, ensure_ascii=False))
        logger.info("=" * 80)
        
        return generated_query
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON Parse Error: {str(e)}")
        logger.error(f"Failed to parse text: {generated_text}")
        raise ValueError(f"Failed to parse generated query as JSON: {str(e)}")
    except Exception as e:
        logger.error(f"Error generating query: {str(e)}")
        raise Exception(f"Error generating query: {str(e)}")



