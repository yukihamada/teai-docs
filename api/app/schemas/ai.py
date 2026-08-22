from pydantic import BaseModel
from typing import List, Optional

class AIRequest(BaseModel):
    messages: List[dict]
    model: str = "gpt-4"
    temperature: float = 0.7
    max_tokens: Optional[int] = None

class AIResponse(BaseModel):
    text: str
    usage: dict
    model: str