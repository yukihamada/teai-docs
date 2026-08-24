from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class SubscriptionCreate(BaseModel):
    plan_id: str
    payment_method_id: Optional[str] = None


class SubscriptionResponse(BaseModel):
    subscription_id: str
    status: str
    current_period_end: Optional[datetime] = None


class UsageCosts(BaseModel):
    ai_usage: float
    instances: float
    storage: float
    total: float
    margin_percentage: float


class FaxUsageCosts(BaseModel):
    fax_count: int
    total_credits: int
    records: list