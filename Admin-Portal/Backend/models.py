from datetime import datetime, timezone
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class AgentBase(BaseModel):
    name: str
    api_key: str
    system_prompt: str
    endpoint: str
    endpoint_info: str
    example_query: Dict[str, Any]
    test_scenarios: str


class AgentCreate(AgentBase):
    pass


class AgentUpdate(BaseModel):
    name: Optional[str] = None
    api_key: Optional[str] = None
    system_prompt: Optional[str] = None
    endpoint: Optional[str] = None
    endpoint_info: Optional[str] = None
    example_query: Optional[Dict[str, Any]] = None
    test_scenarios: Optional[str] = None


class Agent(AgentBase):
    id: Optional[str] = Field(None, alias="_id", serialization_alias="_id")
    created_at: Optional[datetime] = None

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
        json_schema_extra={
            "example": {
                "_id": "507f1f77bcf86cd799439011",
                "name": "MotieChecker",
                "api_key": "sk-XXXXXXXXXXXXXXXXXXXXXXXXXXXX",
                "system_prompt": "You are a political analyst...",
                "endpoint": "https://api.tweedekamer.nl/open_data",
                "endpoint_info": "Tweede Kamer Open Data API",
                "example_query": {
                    "type": "stemming",
                    "query": {"bool": {"must": []}},
                    "size": 1
                },
                "test_scenarios": "User prompt: ...",
                "created_at": "2024-01-01T00:00:00Z"
            }
        }
    )

