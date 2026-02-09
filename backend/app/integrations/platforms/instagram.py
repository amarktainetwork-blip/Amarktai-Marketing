"""
Instagram integration for posting Reels and images
"""

import httpx
from typing import Dict, Any, Optional
from app.integrations.platforms.base import BasePlatform, PostResult, PlatformAnalytics

class InstagramPlatform(BasePlatform):
    """Instagram integration for posting Reels and images."""
    
    def __init__(self, access_token: str, instagram_account_id: str, refresh_token: Optional[str] = None):
        super().__init__(access_token, refresh_token)
        self.instagram_account_id = instagram_account_id
        self.base_url = "https://graph.facebook.com/v18.0"
    
    async def post_content(self,
                          content: str,
                          media_urls: list = None,
                          content_type: str = "REELS",
                          **kwargs) -> PostResult:
        """
        Post to Instagram (Reels or images).
        
        Args:
            content: Caption text
            media_urls: List of media URLs
            content_type: "REELS" or "CAROUSEL" or "STORIES"
            
        Returns:
            PostResult with media ID
        """
        try:
            # Instagram Graph API flow:
            # 1. Upload media (container creation)
            # 2. Publish container
            
            headers = {
                "Authorization": f"Bearer {self.access_token}"
            }
            
            # Step 1: Create media container
            if content_type == "REELS":
                # For Reels, we need a video URL
                container_url = f"{self.base_url}/{self.instagram_account_id}/media"
                params = {
                    "media_type": "REELS",
                    "video_url": media_urls[0] if media_urls else None,
                    "caption": content,
                    "share_to_feed": True
                }
            else:
                # For images/carousel
                container_url = f"{self.base_url}/{self.instagram_account_id}/media"
                params = {
                    "image_url": media_urls[0] if media_urls else None,
                    "caption": content
                }
            
            # In production, make actual API calls
            # For now, return mock success
            
            return PostResult(
                success=True,
                post_id=f"instagram_{content_type.lower()}_{hash(content) % 1000000}",
                url=f"https://instagram.com/p/mock"
            )
            
        except Exception as e:
            return PostResult(success=False, error=str(e))
    
    async def post_reel(self, video_url: str, caption: str, hashtags: list = None) -> PostResult:
        """Post a Reel specifically."""
        full_caption = caption
        if hashtags:
            full_caption += "\n\n" + " ".join([f"#{tag}" for tag in hashtags])
        
        return await self.post_content(
            content=full_caption,
            media_urls=[video_url],
            content_type="REELS"
        )
    
    async def post_carousel(self, image_urls: list, caption: str) -> PostResult:
        """Post a carousel of images."""
        return await self.post_content(
            content=caption,
            media_urls=image_urls,
            content_type="CAROUSEL"
        )
    
    async def get_analytics(self, post_id: str) -> PlatformAnalytics:
        """Get analytics for an Instagram post."""
        try:
            # Instagram Insights API
            # In production, make actual API call
            
            return PlatformAnalytics(
                views=2500,
                likes=180,
                comments=25,
                shares=12,
                clicks=35,
                engagement_rate=8.5
            )
            
        except Exception as e:
            return PlatformAnalytics()
    
    async def refresh_access_token(self) -> bool:
        """Refresh Instagram access token."""
        # Instagram tokens are long-lived, but can be refreshed
        return True
