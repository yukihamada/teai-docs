from pydantic import BaseModel
from typing import List, Optional


class Message(BaseModel):
    role: str
    content: str


class AIRequest(BaseModel):
    messages: List[Message]
    model: Optional[str] = "gpt-3.5-turbo"


class AIResponse(BaseModel):
    text: str
    usage: dict
    model: str