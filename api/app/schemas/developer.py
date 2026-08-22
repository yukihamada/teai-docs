from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ApiKeyCreate(BaseModel):
    name: str
    permissions: List[str] = ["ai:read", "ai:write"]

class ApiKeyResponse(BaseModel):
    api_key: str
    name: str
    created_at: datetime
    permissions: List[str]

class DeveloperProfile(BaseModel):
    user_id: str
    email: str
    api_keys_count: int
    total_requests: int
    total_cost: float
    created_at: datetime

class DeveloperStats(BaseModel):
    requests_today: int
    requests_this_month: int
    cost_today: float
    cost_this_month: float
    top_models: List[str]
    error_rate: float