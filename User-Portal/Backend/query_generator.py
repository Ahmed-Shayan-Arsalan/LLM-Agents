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
    
    # Build OData-specific context if this is an OData endpoint
    odata_context = ""
    if is_odata:
        odata_context = """
IMPORTANT OData API Information:
- This is an OData v4 API at: https://gegevensmagazijn.tweedekamer.nl/OData/v4/2.0/
- Available entity sets include: Stemming (voting records), Besluit (decisions), Zaak (cases), Vergadering (meetings), etc.

EXACT FIELD DEFINITIONS:
- Stemming entity fields: Id, Besluit_Id, Soort, FractieGrootte, ActorNaam, ActorFractie, Vergissing, SidActorLid, SidActorFractie, Persoon_Id, Fractie_Id, GewijzigdOp, ApiGewijzigdOp, Verwijderd
  * NO "Datum" field exists on Stemming
  * NO "Omschrijving" field exists on Stemming
  
- Besluit entity fields: Id, Agendapunt_Id, StemmingsSoort, BesluitSoort, BesluitTekst (description text), Opmerking, Status, AgendapuntZaakBesluitVolgorde, GewijzigdOp, ApiGewijzigdOp, Verwijderd
  * NO "Datum" field exists on Besluit
  * Use "GewijzigdOp" or "ApiGewijzigdOp" for date filtering on Besluit
  * BesluitTekst contains the description/text content

DATE FILTERING:
- For Besluit entity: Use GewijzigdOp or ApiGewijzigdOp (datetime fields)
  Example: ApiGewijzigdOp ge 2022-01-01T00:00:00Z and ApiGewijzigdOp le 2022-12-31T23:59:59Z
- For Stemming entity: Use GewijzigdOp or ApiGewijzigdOp (datetime fields)
  Example: ApiGewijzigdOp ge 2022-01-01T00:00:00Z

QUERY STRATEGY:
- To search voting records by description: Query Besluit entity with BesluitTekst field
- To filter by date: Use GewijzigdOp or ApiGewijzigdOp (NOT "Datum")
- To get voting details: Query Stemming entity and join with Besluit via Besluit_Id

OData $filter syntax examples:
  * contains(BesluitTekst,'studenten') - search in BesluitTekst field
  * ActorFractie eq 'VVD' - exact match (on Stemming entity)
  * ApiGewijzigdOp ge 2022-01-01T00:00:00Z - date filtering (use ISO 8601 format)
  * and/or operators for combining conditions

CRITICAL: Do NOT use "Datum" field - it does not exist. Use "GewijzigdOp" or "ApiGewijzigdOp" instead.
"""
    
    # Build the prompt for query generation - adapt based on example query structure
    system_prompt = f"""You are a query generation assistant. Your job is to convert user queries into API query structures.

Agent Context:
- System Prompt: {agent['system_prompt']}
- Endpoint Info: {agent['endpoint_info']}
- Endpoint URL: {endpoint}
- Example Query: {json.dumps(example_query, indent=2)}
- Test Scenarios: {agent['test_scenarios']}
{odata_context}
CRITICAL INSTRUCTIONS:
1. Analyze the example query structure carefully - it shows the EXACT format this API expects
2. Generate a query that matches the example query structure EXACTLY
3. Adapt the parameters/values to match what the user is asking for
4. If this is an OData endpoint (contains /OData/), generate OData-style queries with correct field names
5. If the example uses "entity_set" and "filter", generate OData-style queries
6. If the example uses "query" with nested objects, generate Elasticsearch-style queries
7. If the example uses a different structure, match that structure exactly
8. Return ONLY valid JSON that matches the example query format
9. Do not include any explanations, comments, or markdown formatting - just the raw JSON
10. IMPORTANT: Use only fields that actually exist in the OData entity (see OData API Information above)

Your task:
1. Analyze the user's query
2. Look at the example query structure - this is the format you MUST follow
3. If this is an OData endpoint, use the correct entity set and field names from the OData API Information
4. Generate an appropriate API query structure that matches the example format
5. Adapt the query parameters to match what the user is asking for
6. Ensure the structure matches the example query exactly (same keys, same nesting)
7. For text searches on voting records, use Besluit entity with BesluitTekst field, or join via Besluit_Id

The query should be structured to retrieve data that will help answer the user's question."""

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



