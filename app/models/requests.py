from pydantic import BaseModel, Field, validator
from typing import Optional

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000, description="User message")
    user_id: Optional[str] = Field(None, max_length=100, description="Optional user ID")
    
    @validator('message')
    def validate_message(cls, v):
        if not v.strip():
            raise ValueError('Message cannot be empty or whitespace only')
        return v.strip()

class ProductSearchRequest(BaseModel):
    q: str = Field(..., min_length=1, max_length=200, description="Search query")
    limit: int = Field(10, ge=1, le=50, description="Number of results")
    
    @validator('q')
    def validate_query(cls, v):
        if not v.strip():
            raise ValueError('Search query cannot be empty')
        return v.strip()