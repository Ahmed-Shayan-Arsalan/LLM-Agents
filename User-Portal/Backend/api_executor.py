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
    is_odata = "/OData/" in endpoint or endpoint.endswith("/OData/v4/2.0") or endpoint.endswith("/OData/v4/2.0/")
    has_odata_structure = "entity_set" in query or "$filter" in str(query) or "filter" in query
    
    try:
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            # Try OData format if detected
            if is_odata or has_odata_structure:
                try:
                    logger.info("Attempting OData-style GET request")
                    
                    # Build OData query URL
                    entity_set = query.get("entity_set", query.get("type", "Stemming"))
                    base_url = endpoint.rstrip("/")
                    
                    # Normalize OData base URL
                    if "/OData/" in base_url:
                        if not base_url.endswith("/OData/v4/2.0"):
                            if base_url.endswith("/OData/v4/2.0/"):
                                base_url = base_url.rstrip("/")
                            elif "/OData/v4/2.0/" in base_url:
                                base_url = base_url.split("/OData/v4/2.0/")[0] + "/OData/v4/2.0"
                            elif "/OData/" in base_url:
                                # Extract base up to /OData/ and add /v4/2.0
                                parts = base_url.split("/OData/")
                                base_url = parts[0] + "/OData/v4/2.0"
                    
                    # Build OData query parameters
                    # OData uses $ prefix which should NOT be encoded
                    # Build URL using httpx.URL to properly handle OData $ parameters
                    entity_url = f"{base_url}/{entity_set}"
                    
                    # Build query parameters dict - httpx will encode values but we need to preserve $ in keys
                    # So we'll build the query string manually
                    odata_parts = []
                    if "filter" in query:
                        # Encode the filter value properly for OData
                        # OData filter syntax: contains(Omschrijving,'studentenhuisvesting') and Datum ge 2022-01-01
                        # We need to encode spaces and special chars but preserve OData operators
                        filter_value = query['filter']
                        # Encode the filter value - preserve OData operators and syntax
                        # OData operators: and, or, ge, le, gt, lt, eq, ne, contains, startswith, endswith
                        # Keep parentheses, quotes, commas, and operators unencoded
                        # Spaces need to be encoded as %20
                        filter_value = quote(filter_value, safe="'(),andorgelegtlteqnecontainsstartswithendswith")
                        odata_parts.append(f"$filter={filter_value}")
                    if "top" in query:
                        odata_parts.append(f"$top={query['top']}")
                    elif "size" in query:
                        odata_parts.append(f"$top={query['size']}")
                    if "select" in query:
                        # Select fields - encode but preserve commas
                        select_value = quote(query['select'], safe=",")
                        odata_parts.append(f"$select={select_value}")
                    if "orderby" in query:
                        # Orderby - encode but preserve spaces
                        orderby_value = quote(query['orderby'], safe=" ")
                        odata_parts.append(f"$orderby={orderby_value}")
                    
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
                        # 400 Bad Request - likely URL encoding issue, log error details
                        error_text = response.text[:500] if hasattr(response, 'text') else "No error details"
                        logger.error(f"OData GET returned 400 Bad Request")
                        logger.error(f"Error details: {error_text}")
                        logger.error(f"Attempted URL: {full_url}")
                        # Don't fallback - 400 means the request format is wrong
                        raise Exception(f"OData API returned 400 Bad Request. Check query format. Error: {error_text}")
                    else:
                        # If GET failed with other status, fall through to try POST
                        logger.warning(f"OData GET returned status {response.status_code}, trying POST fallback...")
                        raise httpx.HTTPStatusError("Trying POST fallback", request=response.request, response=response)
                        
                except httpx.HTTPStatusError as e:
                    # Only fallback to POST if it's a 405, not for 400 errors
                    if e.response.status_code == 405:
                        logger.info("OData GET returned 405, falling back to POST method")
                    elif e.response.status_code == 400:
                        # Re-raise 400 errors - they indicate format issues
                        raise
                    else:
                        logger.warning(f"OData GET failed with status {e.response.status_code}, trying POST fallback...")
                    # Fall through to POST attempt only for 405
                    if e.response.status_code != 405:
                        raise
                except httpx.RequestError as e:
                    logger.warning(f"OData GET request error: {str(e)}, trying POST fallback...")
                    # Fall through to POST attempt
            
            # Standard API - use POST with JSON body (default or fallback)
            logger.info("Using POST request with JSON body")
            logger.info(f"Request URL: {endpoint}")
            logger.info(f"Request Method: POST")
            
            response = await client.post(
                endpoint,
                json=query,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                    "User-Agent": "LLM-Agents/1.0"
                }
            )
            
            logger.info(f"API Response Status: {response.status_code}")
            logger.info(f"Response Headers: {dict(response.headers)}")
            
            # If POST also fails with 405, try GET as last resort (only for non-OData)
            if response.status_code == 405 and not (is_odata or has_odata_structure):
                logger.warning("POST returned 405 Method Not Allowed, trying GET as fallback...")
                # Try GET with query as URL parameters
                get_url = endpoint
                if query:
                    # Convert query dict to URL parameters
                    params = []
                    for key, value in query.items():
                        if isinstance(value, (str, int, float, bool)):
                            params.append(f"{key}={quote(str(value))}")
                        elif isinstance(value, dict):
                            params.append(f"{key}={quote(json.dumps(value))}")
                    if params:
                        get_url = f"{endpoint}?{'&'.join(params)}"
                
                logger.info(f"Fallback GET URL: {get_url}")
                response = await client.get(
                    get_url,
                    headers={
                        "Accept": "application/json",
                        "User-Agent": "LLM-Agents/1.0"
                    }
                )
                logger.info(f"Fallback GET Response Status: {response.status_code}")
            
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



