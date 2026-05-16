from pydantic import BaseModel, Field, validator
from typing import List, Optional

class ChatRequest(BaseModel):
    query: str = Field(..., max_length=1000, example="What is the NAV of HDFC Mid Cap Fund?")
    user_id: Optional[str] = Field(None, example="user_1")
    session_id: Optional[str] = Field(None, example="session_abc123")

    @validator("query")
    def not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("Query cannot be empty")
        return v

class SourceChunk(BaseModel):
    fund_name: str
    chunk_id: Optional[int] = None
    score: float
    text: str

class ChatResponse(BaseModel):
    answer: str
    sources: List[SourceChunk]
    disclaimer: Optional[str] = None
