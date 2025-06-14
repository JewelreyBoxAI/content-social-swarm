"""
Facebook Platform Agent for ContentSocialSwarm.

Handles Facebook page management, content publishing, and analytics
through Facebook Graph API with MCP integration.
"""

import logging
from typing import Any, Dict, List, Optional
import facebook
from src.config.settings import get_settings

logger = logging.getLogger(__name__)


class FacebookAgent:
    """Facebook platform agent for content management."""
    
    def __init__(self):
        self.settings = get_settings()
        self.graph = None
        
    async def initialize(self):
        """Initialize Facebook Graph API connection."""
        try:
            self.graph = facebook.GraphAPI(
                access_token=self.settings.FACEBOOK_ACCESS_TOKEN,
                version="18.0"
            )
            logger.info("Facebook Agent initialized successfully")
        except Exception as e:
            logger.error(f"Facebook Agent initialization failed: {str(e)}")
            
    async def shutdown(self):
        """Cleanup Facebook agent resources."""
        self.graph = None
        logger.info("Facebook Agent shutdown complete")
        
    async def optimize_content(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize content for Facebook platform."""
        # Facebook-specific optimizations
        optimized = content.copy()
        
        # Limit text length for better engagement
        if len(optimized.get("text", "")) > 500:
            optimized["text"] = optimized["text"][:497] + "..."
            
        # Ensure hashtags are included but not excessive
        hashtags = optimized.get("hashtags", [])
        if len(hashtags) > 5:
            optimized["hashtags"] = hashtags[:5]
            
        return optimized
        
    async def publish_content(self, content: Dict[str, Any], client_id: str) -> Dict[str, Any]:
        """Publish content to Facebook."""
        try:
            if not self.graph:
                raise Exception("Facebook Graph API not initialized")
                
            # Prepare post data
            post_data = {
                "message": content.get("text", "")
            }
            
            # Add image if available
            if content.get("image_url"):
                post_data["link"] = content["image_url"]
                
            # Publish to page (assuming page access)
            result = self.graph.put_object(
                parent_object="me",
                connection_name="feed",
                **post_data
            )
            
            return {
                "status": "success",
                "platform": "facebook",
                "post_id": result.get("id"),
                "client_id": client_id
            }
            
        except Exception as e:
            logger.error(f"Facebook publishing failed: {str(e)}")
            return {
                "status": "failed",
                "platform": "facebook",
                "error": str(e),
                "client_id": client_id
            }
            
    async def get_analytics(self, post_id: str) -> Dict[str, Any]:
        """Get analytics for a specific Facebook post."""
        try:
            if not self.graph:
                raise Exception("Facebook Graph API not initialized")
                
            # Get post insights
            insights = self.graph.get_object(
                id=f"{post_id}/insights",
                metric="post_impressions,post_engaged_users,post_clicks"
            )
            
            return {
                "platform": "facebook",
                "post_id": post_id,
                "insights": insights
            }
            
        except Exception as e:
            logger.error(f"Facebook analytics failed: {str(e)}")
            return {
                "platform": "facebook",
                "post_id": post_id,
                "error": str(e)
            } 