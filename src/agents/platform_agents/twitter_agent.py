"""
Twitter/X Platform Agent for ContentSocialSwarm.

Handles Twitter content publishing, threading, and analytics
through Twitter API v2 with MCP integration.
"""

import logging
from typing import Any, Dict, List, Optional
import tweepy
from src.config.settings import get_settings

logger = logging.getLogger(__name__)


class TwitterAgent:
    """Twitter/X platform agent for content management."""
    
    def __init__(self):
        self.settings = get_settings()
        self.client = None
        
    async def initialize(self):
        """Initialize Twitter API connection."""
        try:
            self.client = tweepy.Client(
                bearer_token=self.settings.TWITTER_BEARER_TOKEN,
                consumer_key=self.settings.TWITTER_API_KEY,
                consumer_secret=self.settings.TWITTER_API_SECRET,
                access_token=self.settings.TWITTER_ACCESS_TOKEN,
                access_token_secret=self.settings.TWITTER_ACCESS_TOKEN_SECRET,
                wait_on_rate_limit=True
            )
            
            # Verify credentials
            me = self.client.get_me()
            if me.data:
                logger.info("Twitter Agent initialized successfully")
            else:
                logger.error("Twitter Agent initialization failed: Unable to verify credentials")
                
        except Exception as e:
            logger.error(f"Twitter Agent initialization failed: {str(e)}")
            
    async def shutdown(self):
        """Cleanup Twitter agent resources."""
        self.client = None
        logger.info("Twitter Agent shutdown complete")
        
    async def optimize_content(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize content for Twitter platform."""
        optimized = content.copy()
        
        # Twitter has a 280 character limit
        text = optimized.get("text", "")
        hashtags = optimized.get("hashtags", [])
        
        # Calculate space needed for hashtags
        hashtag_text = " ".join(f"#{tag}" for tag in hashtags[:5])  # Limit to 5 hashtags
        available_chars = 280 - len(hashtag_text) - 2  # -2 for space and newline
        
        if len(text) > available_chars:
            optimized["text"] = text[:available_chars-3] + "..."
            
        # Limit hashtags for Twitter
        optimized["hashtags"] = hashtags[:5]
            
        return optimized
        
    async def publish_content(self, content: Dict[str, Any], client_id: str) -> Dict[str, Any]:
        """Publish content to Twitter."""
        try:
            if not self.client:
                raise Exception("Twitter client not initialized")
                
            # Prepare tweet text
            text = content.get("text", "")
            hashtags = content.get("hashtags", [])
            
            if hashtags:
                hashtag_text = " ".join(f"#{tag}" for tag in hashtags)
                tweet_text = f"{text}\n\n{hashtag_text}"
            else:
                tweet_text = text
                
            # Ensure tweet is within character limit
            if len(tweet_text) > 280:
                tweet_text = tweet_text[:277] + "..."
                
            # Post tweet
            response = self.client.create_tweet(text=tweet_text)
            
            if response.data:
                return {
                    "status": "success",
                    "platform": "twitter",
                    "post_id": response.data['id'],
                    "client_id": client_id,
                    "text": tweet_text
                }
            else:
                raise Exception("Tweet creation failed - no response data")
            
        except Exception as e:
            logger.error(f"Twitter publishing failed: {str(e)}")
            return {
                "status": "failed",
                "platform": "twitter",
                "error": str(e),
                "client_id": client_id
            }
            
    async def get_analytics(self, post_id: str) -> Dict[str, Any]:
        """Get analytics for a specific Twitter post."""
        try:
            if not self.client:
                raise Exception("Twitter client not initialized")
                
            # Get tweet metrics
            tweet = self.client.get_tweet(
                id=post_id,
                tweet_fields=["public_metrics", "created_at"]
            )
            
            if tweet.data:
                metrics = tweet.data.public_metrics
                return {
                    "platform": "twitter",
                    "post_id": post_id,
                    "insights": {
                        "retweets": metrics.get("retweet_count", 0),
                        "likes": metrics.get("like_count", 0),
                        "replies": metrics.get("reply_count", 0),
                        "quotes": metrics.get("quote_count", 0),
                        "impressions": metrics.get("impression_count", 0)
                    }
                }
            else:
                raise Exception("Unable to fetch tweet data")
            
        except Exception as e:
            logger.error(f"Twitter analytics failed: {str(e)}")
            return {
                "platform": "twitter",
                "post_id": post_id,
                "error": str(e)
            } 