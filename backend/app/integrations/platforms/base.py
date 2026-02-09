"""
Base class for social media platform integrations
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class PostResult:
    success: bool
    post_id: Optional[str] = None
    error: Optional[str] = None
    url: Optional[str] = None

@dataclass
class PlatformAnalytics:
    views: int = 0
    likes: int = 0
    comments: int = 0
    shares: int = 0
    clicks: int = 0
    engagement_rate: float = 0.0

class BasePlatform(ABC):
    """Base class for social media platform integrations."""
    
    def __init__(self, access_token: str, refresh_token: Optional[str] = None):
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.base_url = ""
    
    @abstractmethod
    async def post_content(self, 
                          content: str, 
                          media_urls: list = None,
                          **kwargs) -> PostResult:
        """Post content to the platform."""
        pass
    
    @abstractmethod
    async def get_analytics(self, post_id: str) -> PlatformAnalytics:
        """Get analytics for a post."""
        pass
    
    @abstractmethod
    async def refresh_access_token(self) -> bool:
        """Refresh the access token."""
        pass
    
    async def validate_token(self) -> bool:
        """Validate the current access token."""
        return True
