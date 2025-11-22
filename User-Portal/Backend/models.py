from pydantic import BaseModel
from typing import Dict, Any, Optional


class QueryGenerationRequest(BaseModel):
    agent_name: str
    user_query: str


class QueryGenerationResponse(BaseModel):
    generated_query: Dict[str, Any]
    success: bool
    message: Optional[str] = None


class OpenAIRequest(BaseModel):
    agent_name: str
    user_query: str
    api_results: Dict[str, Any]


class OpenAIResponse(BaseModel):
    response: str
    success: bool
    message: Optional[str] = None



