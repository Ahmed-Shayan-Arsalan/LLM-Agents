"""
API Executor Module
Handles execution of queries against external APIs
"""
import httpx
from typing import Dict, Any
from database import collection
import logging
import json
from datetime import datetime
from urllib.parse import quote, urlencode

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


async def execute_query(agent_name: str, query: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute a query against the agent's endpoint
    
    Args:
        agent_name: Name of the agent
        query: Query dictionary to send to the endpoint
        
    Returns:
        API response data
    """
    logger.info("=" * 80)
    logger.info(f"API EXECUTION STARTED - Agent: {agent_name}")
    logger.info(f"Timestamp: {datetime.now().isoformat()}")
    logger.info("-" * 80)
    
    # Get agent configuration
    agent = get_agent_by_name(agent_name)
    endpoint = agent["endpoint"]
    
    logger.info(f"Endpoint: {endpoint}")
    logger.info("-" * 80)
    logger.info("QUERY BEING SENT TO API:")
    logger.info(json.dumps(query, indent=2, ensure_ascii=False))
    logger.info("-" * 80)
    
    # Detect endpoint type based on URL and query structure
    # OData detection: look for /OData/ or /odata/ (case-insensitive)
    is_odata = "/odata/" in endpoint.lower()
    has_odata_structure = "entity_set" in query or "$filter" in str(query) or "filter" in query
    
    try:
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            # ALWAYS use GET requests - convert query to URL parameters
            # OData has special handling for $ parameters
            if is_odata or has_odata_structure:
                try:
                    logger.info("Attempting OData-style GET request")
                    
                    # Build OData query URL
                    # Get entity_set from query, or use 'type' field as fallback
                    entity_set = query.get("entity_set") or query.get("type")
                    
                    if not entity_set:
                        raise ValueError("OData query must include 'entity_set' or 'type' field to specify the entity to query")
                    
                    # Normalize endpoint URL - remove trailing slashes
                    base_url = endpoint.rstrip("/")
                    
                    # Build OData query URL with entity set
                    entity_url = f"{base_url}/{entity_set}"
                    
                    # Build OData query parameters
                    # OData uses $ prefix which should NOT be encoded in the parameter names
                    # We'll build the query string manually to preserve $ signs
                    odata_parts = []
                    
                    # Handle $filter parameter
                    if "filter" in query:
                        filter_value = query['filter']
                        # Encode the filter value - preserve OData operators and syntax
                        # OData operators: and, or, not, ge, le, gt, lt, eq, ne, contains, startswith, endswith
                        # Keep parentheses, quotes, commas, and operators unencoded
                        # Spaces and special characters will be encoded
                        filter_value = quote(filter_value, safe="'(),andorgelegtlteqnecontainsstartswithendswith")
                        odata_parts.append(f"$filter={filter_value}")
                    
                    # Handle $top parameter (limit results)
                    if "top" in query:
                        odata_parts.append(f"$top={query['top']}")
                    elif "size" in query:  # Allow 'size' as alias for $top
                        odata_parts.append(f"$top={query['size']}")
                    
                    # Handle $skip parameter (pagination)
                    if "skip" in query:
                        odata_parts.append(f"$skip={query['skip']}")
                    elif "from" in query:  # Allow 'from' as alias for $skip
                        odata_parts.append(f"$skip={query['from']}")
                    
                    # Handle $select parameter (field selection)
                    if "select" in query:
                        # Select fields - encode but preserve commas
                        select_value = quote(query['select'], safe=",")
                        odata_parts.append(f"$select={select_value}")
                    
                    # Handle $orderby parameter (sorting)
                    if "orderby" in query:
                        # Orderby - encode but preserve spaces and desc/asc keywords
                        orderby_value = quote(query['orderby'], safe=" ,desasc")
                        odata_parts.append(f"$orderby={orderby_value}")
                    
                    # Handle $expand parameter (related entities)
                    if "expand" in query:
                        expand_value = quote(query['expand'], safe=",/")
                        odata_parts.append(f"$expand={expand_value}")
                    
                    # Build full URL - manually construct to preserve $ in parameter names
                    if odata_parts:
                        query_string = "&".join(odata_parts)
                        full_url = f"{entity_url}?{query_string}"
                    else:
                        full_url = entity_url
                    
                    logger.info(f"Request URL: {full_url}")
                    logger.info(f"Request Method: GET")
                    logger.info(f"OData Parameters: {query_string if odata_parts else 'None'}")
                    
                    # Use the raw URL string directly
                    # httpx.request() with a full URL string should preserve the query string as-is
                    # But we need to ensure httpx doesn't re-encode it
                    # The issue is that httpx.URL() might encode $ signs, so we'll use the string directly
                    response = await client.get(
                        full_url,
                        headers={
                            "Accept": "application/json",
                            "User-Agent": "LLM-Agents/1.0"
                        },
                        follow_redirects=True
                    )
                    
                    logger.info(f"API Response Status: {response.status_code}")
                    
                    # If successful, return results
                    if response.status_code == 200:
                        response.raise_for_status()
                        api_results = response.json()
                        logger.info("-" * 80)
                        logger.info("API RESPONSE RECEIVED (OData GET):")
                        response_str = json.dumps(api_results, indent=2, ensure_ascii=False)
                        if len(response_str) > 1000:
                            logger.info(response_str[:1000] + f"\n... (truncated, total length: {len(response_str)} chars)")
                        else:
                            logger.info(response_str)
                        logger.info("=" * 80)
                        return api_results
                    elif response.status_code == 400:
                        # 400 Bad Request - query format issue
                        error_text = response.text[:500] if hasattr(response, 'text') else "No error details"
                        logger.error(f"OData GET returned 400 Bad Request")
                        logger.error(f"Error details: {error_text}")
                        logger.error(f"Attempted URL: {full_url}")
                        # Don't fallback for 400 - it means the query format is wrong
                        raise Exception(f"OData API returned 400 Bad Request. The query format may be incorrect. Error: {error_text}")
                    elif response.status_code == 404:
                        # 404 Not Found - entity set or endpoint doesn't exist
                        error_text = response.text[:500] if hasattr(response, 'text') else "No error details"
                        logger.error(f"OData GET returned 404 Not Found")
                        logger.error(f"Error details: {error_text}")
                        logger.error(f"Attempted URL: {full_url}")
                        raise Exception(f"OData endpoint or entity set not found (404). Check entity_set name. Error: {error_text}")
                    else:
                        # Other status codes - raise error (no fallback)
                        error_text = response.text[:500] if hasattr(response, 'text') else "No error details"
                        logger.error(f"OData GET returned status {response.status_code}")
                        logger.error(f"Error details: {error_text}")
                        raise Exception(f"OData API returned status {response.status_code}. Error: {error_text}")
                        
                except ValueError as e:
                    # Re-raise ValueError (missing entity_set)
                    logger.error(f"OData query configuration error: {str(e)}")
                    raise
                except httpx.HTTPStatusError as e:
                    # Handle HTTP errors - no fallback, just raise
                    error_text = e.response.text[:500] if hasattr(e.response, 'text') else "No error details"
                    logger.error(f"OData GET HTTP error: Status {e.response.status_code}")
                    logger.error(f"Error details: {error_text}")
                    raise Exception(f"OData API request failed with status {e.response.status_code}. Error: {error_text}")
                except httpx.RequestError as e:
                    # Network/connection errors - raise without fallback
                    logger.error(f"OData GET request error: {str(e)}")
                    raise Exception(f"OData API connection error: {str(e)}")
            
            # ALWAYS use GET requests - convert query to URL parameters
            logger.info("Using GET request with URL parameters (standard REST API)")
            logger.info(f"Request URL: {endpoint}")
            logger.info(f"Request Method: GET")
            
            # Convert query dict to URL parameters
            get_url = endpoint
            if query:
                params = []
                for key, value in query.items():
                    if isinstance(value, (str, int, float, bool)):
                        # Simple values - URL encode
                        params.append(f"{key}={quote(str(value))}")
                    elif isinstance(value, dict):
                        # Nested dicts - JSON encode and URL encode
                        params.append(f"{key}={quote(json.dumps(value))}")
                    elif isinstance(value, list):
                        # Arrays - repeat parameter for each item
                        for item in value:
                            if isinstance(item, (str, int, float, bool)):
                                params.append(f"{key}={quote(str(item))}")
                            else:
                                params.append(f"{key}={quote(json.dumps(item))}")
                    elif value is None:
                        # Skip None values
                        continue
                
                if params:
                    query_string = "&".join(params)
                    get_url = f"{endpoint}?{query_string}"
                    logger.info(f"Query Parameters: {query_string[:200]}...")
            
            logger.info(f"Full Request URL: {get_url}")
            
            response = await client.get(
                get_url,
                headers={
                    "Accept": "application/json",
                    "User-Agent": "LLM-Agents/1.0"
                }
            )
            
            logger.info(f"API Response Status: {response.status_code}")
            logger.info(f"Response Headers: {dict(response.headers)}")
            
            response.raise_for_status()
            api_results = response.json()
            
            logger.info("-" * 80)
            logger.info("API RESPONSE RECEIVED:")
            # Log first 1000 chars of response to avoid huge logs
            response_str = json.dumps(api_results, indent=2, ensure_ascii=False)
            if len(response_str) > 1000:
                logger.info(response_str[:1000] + f"\n... (truncated, total length: {len(response_str)} chars)")
            else:
                logger.info(response_str)
            logger.info("=" * 80)
            
            return api_results
    except httpx.HTTPStatusError as e:
        logger.error(f"API HTTP Error: Status {e.response.status_code}")
        logger.error(f"Response Text: {e.response.text}")
        raise Exception(f"API request failed with status {e.response.status_code}: {e.response.text}")
    except httpx.TimeoutException:
        logger.error("API request timed out after 30 seconds")
        raise Exception("API request timed out")
    except Exception as e:
        logger.error(f"Error executing API query: {str(e)}")
        raise Exception(f"Error executing API query: {str(e)}")



