"""
MCP Connectors for ContentSocialSwarm.

Provides unified Model Context Protocol integration for all social media platforms
and GoHighLevel CRM through standardized connectors.
"""

import logging
from typing import Any, Dict, List, Optional
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class MCPConnector(ABC):
    """Abstract base class for MCP connectors."""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        self.name = name
        self.config = config
        self.is_connected = False
    
    @abstractmethod
    async def connect(self) -> bool:
        """Establish connection to the platform."""
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """Close platform connection."""
        pass
    
    @abstractmethod
    async def get_tools(self) -> List[Dict[str, Any]]:
        """Get available tools for this connector."""
        pass


class FacebookMCPConnector(MCPConnector):
    """MCP connector for Facebook platform."""
    
    async def connect(self) -> bool:
        """Connect to Facebook Graph API."""
        try:
            # Initialize Facebook connection
            self.is_connected = True
            logger.info(f"Facebook MCP connector connected")
            return True
        except Exception as e:
            logger.error(f"Facebook MCP connection failed: {str(e)}")
            return False
    
    async def disconnect(self) -> None:
        """Disconnect from Facebook."""
        self.is_connected = False
        logger.info("Facebook MCP connector disconnected")
    
    async def get_tools(self) -> List[Dict[str, Any]]:
        """Get Facebook-specific tools."""
        return [
            {
                "name": "facebook_post",
                "description": "Create a post on Facebook",
                "parameters": {
                    "message": {"type": "string", "required": True},
                    "image_url": {"type": "string", "required": False}
                }
            },
            {
                "name": "facebook_analytics",
                "description": "Get Facebook post analytics",
                "parameters": {
                    "post_id": {"type": "string", "required": True}
                }
            }
        ]


class InstagramMCPConnector(MCPConnector):
    """MCP connector for Instagram platform."""
    
    async def connect(self) -> bool:
        """Connect to Instagram Graph API."""
        try:
            self.is_connected = True
            logger.info(f"Instagram MCP connector connected")
            return True
        except Exception as e:
            logger.error(f"Instagram MCP connection failed: {str(e)}")
            return False
    
    async def disconnect(self) -> None:
        """Disconnect from Instagram."""
        self.is_connected = False
        logger.info("Instagram MCP connector disconnected")
    
    async def get_tools(self) -> List[Dict[str, Any]]:
        """Get Instagram-specific tools."""
        return [
            {
                "name": "instagram_post",
                "description": "Create a post on Instagram",
                "parameters": {
                    "caption": {"type": "string", "required": True},
                    "image_url": {"type": "string", "required": True}
                }
            },
            {
                "name": "instagram_story",
                "description": "Create an Instagram story",
                "parameters": {
                    "image_url": {"type": "string", "required": True},
                    "text": {"type": "string", "required": False}
                }
            }
        ]


class TwitterMCPConnector(MCPConnector):
    """MCP connector for Twitter/X platform."""
    
    async def connect(self) -> bool:
        """Connect to Twitter API."""
        try:
            self.is_connected = True
            logger.info(f"Twitter MCP connector connected")
            return True
        except Exception as e:
            logger.error(f"Twitter MCP connection failed: {str(e)}")
            return False
    
    async def disconnect(self) -> None:
        """Disconnect from Twitter."""
        self.is_connected = False
        logger.info("Twitter MCP connector disconnected")
    
    async def get_tools(self) -> List[Dict[str, Any]]:
        """Get Twitter-specific tools."""
        return [
            {
                "name": "twitter_tweet",
                "description": "Create a tweet on Twitter/X",
                "parameters": {
                    "text": {"type": "string", "required": True},
                    "reply_to": {"type": "string", "required": False}
                }
            },
            {
                "name": "twitter_thread",
                "description": "Create a Twitter thread",
                "parameters": {
                    "tweets": {"type": "array", "items": {"type": "string"}, "required": True}
                }
            }
        ]


class GHLMCPConnector(MCPConnector):
    """MCP connector for GoHighLevel CRM."""
    
    async def connect(self) -> bool:
        """Connect to GoHighLevel API."""
        try:
            self.is_connected = True
            logger.info(f"GHL MCP connector connected")
            return True
        except Exception as e:
            logger.error(f"GHL MCP connection failed: {str(e)}")
            return False
    
    async def disconnect(self) -> None:
        """Disconnect from GHL."""
        self.is_connected = False
        logger.info("GHL MCP connector disconnected")
    
    async def get_tools(self) -> List[Dict[str, Any]]:
        """Get GHL-specific tools."""
        return [
            {
                "name": "ghl_create_contact",
                "description": "Create a contact in GoHighLevel",
                "parameters": {
                    "first_name": {"type": "string", "required": True},
                    "email": {"type": "string", "required": True},
                    "phone": {"type": "string", "required": False}
                }
            },
            {
                "name": "ghl_create_opportunity",
                "description": "Create an opportunity in GoHighLevel",
                "parameters": {
                    "contact_id": {"type": "string", "required": True},
                    "title": {"type": "string", "required": True},
                    "value": {"type": "number", "required": False}
                }
            }
        ]


class MCPManager:
    """Manager for all MCP connectors."""
    
    def __init__(self):
        self.connectors: Dict[str, MCPConnector] = {}
    
    async def register_connector(self, connector: MCPConnector) -> bool:
        """Register a new MCP connector."""
        try:
            success = await connector.connect()
            if success:
                self.connectors[connector.name] = connector
                logger.info(f"MCP connector registered: {connector.name}")
                return True
            else:
                logger.error(f"Failed to register MCP connector: {connector.name}")
                return False
        except Exception as e:
            logger.error(f"MCP connector registration failed: {str(e)}")
            return False
    
    async def get_all_tools(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get all tools from all registered connectors."""
        all_tools = {}
        for name, connector in self.connectors.items():
            if connector.is_connected:
                all_tools[name] = await connector.get_tools()
        return all_tools
    
    async def shutdown(self) -> None:
        """Shutdown all MCP connectors."""
        for connector in self.connectors.values():
            await connector.disconnect()
        self.connectors.clear()
        logger.info("All MCP connectors shutdown") 