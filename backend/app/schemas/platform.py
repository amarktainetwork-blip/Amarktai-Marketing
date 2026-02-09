from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.models.platform_connection import PlatformType

class PlatformConnectionBase(BaseModel):
    platform: PlatformType
    account_name: str
    account_id: str
    is_active: bool = True

class PlatformConnectionCreate(PlatformConnectionBase):
    pass

class PlatformConnection(PlatformConnectionBase):
    id: str
    user_id: str
    connected_at: datetime
    expires_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
