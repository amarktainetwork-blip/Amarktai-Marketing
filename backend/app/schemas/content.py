from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from app.models.content import ContentStatus, ContentType

class ContentPerformance(BaseModel):
    views: int = 0
    likes: int = 0
    comments: int = 0
    shares: int = 0
    clicks: int = 0
    ctr: float = 0.0

class ContentBase(BaseModel):
    platform: str
    type: ContentType
    title: str
    caption: str
    hashtags: List[str] = []
    media_urls: List[str] = []

class ContentCreate(ContentBase):
    webapp_id: str

class ContentUpdate(BaseModel):
    caption: Optional[str] = None
    hashtags: Optional[List[str]] = None
    status: Optional[ContentStatus] = None
    scheduled_for: Optional[datetime] = None

class Content(ContentBase):
    id: str
    user_id: str
    webapp_id: str
    status: ContentStatus
    scheduled_for: Optional[datetime] = None
    posted_at: Optional[datetime] = None
    platform_post_id: Optional[str] = None
    performance: Optional[ContentPerformance] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
