from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


class TopicBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    content: Optional[str] = None


class TopicCreate(TopicBase):
    pass


class TopicUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    content: Optional[str] = None


class Topic(TopicBase):
    id: int
    user_id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class TopicSearchRequest(BaseModel):
    query: str = Field(..., min_length=1)


class TopicExplanationRequest(BaseModel):
    topic: str = Field(..., min_length=1)
