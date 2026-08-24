from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class FaxProvider(str, Enum):
    TELNYX = "telnyx"
    PHAXIO = "phaxio"


class FaxSendRequest(BaseModel):
    to: str = Field(..., description="Destination fax number in E.164 format (e.g., +81459490756)")
    media_url: str = Field(..., description="URL to the PDF/document to fax")
    provider: FaxProvider = Field(default=FaxProvider.TELNYX, description="Fax provider to use")
    quality: str = Field(default="high", description="Fax quality: standard, high, fine")
    store_media: bool = Field(default=False, description="Whether to store media after sending")
    monochrome: bool = Field(default=True, description="Send as monochrome")


class FaxSendResponse(BaseModel):
    success: bool
    fax_id: Optional[str] = None
    status: Optional[str] = None
    provider: FaxProvider
    message: Optional[str] = None
    cost_credits: int = 1


class FaxStatusResponse(BaseModel):
    fax_id: str
    status: str
    provider: FaxProvider
    to: str
    from_number: Optional[str] = None
    media_url: Optional[str] = None
    pages: Optional[int] = None
    cost_credits: int = 1
    created_at: Optional[str] = None
    completed_at: Optional[str] = None
    error_message: Optional[str] = None


class FaxUsageRecord(BaseModel):
    fax_id: str
    user_id: int
    provider: FaxProvider
    to_number: str
    pages: int
    cost_credits: int
    status: str
    timestamp: str


class FaxLimitCheck(BaseModel):
    can_send: bool
    daily_sent: int
    daily_limit: int
    has_custom_key: bool
    message: Optional[str] = None