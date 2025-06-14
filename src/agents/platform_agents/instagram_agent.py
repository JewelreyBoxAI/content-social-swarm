"""
Instagram Platform Agent for ContentSocialSwarm.

Handles Instagram content publishing, stories, reels, and analytics
through Instagram Basic Display API and Graph API with MCP integration.
"""

import logging
from typing import Any, Dict, List, Optional
import requests
from src.config.settings import get_settings

logger = logging.getLogger(__name__)


class InstagramAgent:
    """Instagram platform agent for content management."""
    
    def __init__(self):
        self.settings = get_settings()
        self.base_url = "https://graph.instagram.com"
        
    async def initialize(self):
        """Initialize Instagram API connection."""
        try:
            # Verify access token
            if self.settings.FACEBOOK_ACCESS_TOKEN:
                response = requests.get(
                    f"{self.base_url}/me",
                    params={"access_token": self.settings.FACEBOOK_ACCESS_TOKEN}
                )
                if response.status_code == 200:
                    logger.info("Instagram Agent initialized successfully")
                else:
                    logger.error(f"Instagram Agent initialization failed: {response.text}")
            else:
                logger.warning("Instagram access token not configured")
        except Exception as e:
            logger.error(f"Instagram Agent initialization failed: {str(e)}")
            
    async def shutdown(self):
        """Cleanup Instagram agent resources."""
        logger.info("Instagram Agent shutdown complete")
        
    async def optimize_content(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize content for Instagram platform."""
        optimized = content.copy()
        
        # Instagram prefers shorter captions with more hashtags
        if len(optimized.get("text", "")) > 300:
            optimized["text"] = optimized["text"][:297] + "..."
            
        # Instagram allows up to 30 hashtags
        hashtags = optimized.get("hashtags", [])
        if len(hashtags) > 30:
            optimized["hashtags"] = hashtags[:30]
        elif len(hashtags) < 10:
            # Add some generic hashtags if too few
            generic_hashtags = ["#marketing", "#business", "#socialmedia", "#content"]
            optimized["hashtags"] = hashtags + generic_hashtags[:10-len(hashtags)]
            
        return optimized
        
    async def publish_content(self, content: Dict[str, Any], client_id: str) -> Dict[str, Any]:
        """Publish content to Instagram."""
        try:
            if not self.settings.FACEBOOK_ACCESS_TOKEN:
                raise Exception("Instagram access token not configured")
                
            # Prepare caption with hashtags
            caption = content.get("text", "")
            hashtags = content.get("hashtags", [])
            if hashtags:
                caption += "\n\n" + " ".join(f"#{tag}" for tag in hashtags)
                
            # For now, return a simulated success
            # In production, you would use the Instagram Graph API
            return {
                "status": "success",
                "platform": "instagram",
                "post_id": f"ig_{client_id}_{hash(caption) % 10000}",
                "client_id": client_id,
                "caption": caption
            }
            
        except Exception as e:
            logger.error(f"Instagram publishing failed: {str(e)}")
            return {
                "status": "failed",
                "platform": "instagram",
                "error": str(e),
                "client_id": client_id
            }
            
    async def get_analytics(self, post_id: str) -> Dict[str, Any]:
        """Get analytics for a specific Instagram post."""
        try:
            # Simulate analytics data
            # In production, use Instagram Graph API insights
            return {
                "platform": "instagram",
                "post_id": post_id,
                "insights": {
                    "impressions": 1250,
                    "reach": 980,
                    "likes": 45,
                    "comments": 8,
                    "saves": 12
                }
            }
            
        except Exception as e:
            logger.error(f"Instagram analytics failed: {str(e)}")
            return {
                "platform": "instagram",
                "post_id": post_id,
                "error": str(e)
            } 