"""
GoHighLevel (GHL) Agent for ContentSocialSwarm.

Handles GoHighLevel CRM integration, lead management, and automation
through GHL API with MCP integration.
"""

import logging
from typing import Any, Dict, List, Optional
import requests
from datetime import datetime
from src.config.settings import get_settings

logger = logging.getLogger(__name__)


class GHLAgent:
    """GoHighLevel CRM agent for lead and campaign management."""
    
    def __init__(self):
        self.settings = get_settings()
        self.base_url = self.settings.GHL_BASE_URL
        self.headers = {
            "Authorization": f"Bearer {self.settings.GHL_API_KEY}",
            "Content-Type": "application/json"
        }
        
    async def initialize(self):
        """Initialize GHL API connection."""
        try:
            # Test API connection
            response = requests.get(
                f"{self.base_url}/locations/",
                headers=self.headers
            )
            
            if response.status_code == 200:
                logger.info("GHL Agent initialized successfully")
            else:
                logger.error(f"GHL Agent initialization failed: {response.text}")
                
        except Exception as e:
            logger.error(f"GHL Agent initialization failed: {str(e)}")
            
    async def shutdown(self):
        """Cleanup GHL agent resources."""
        logger.info("GHL Agent shutdown complete")
        
    async def update_campaign_results(self, client_id: str, campaign_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update GHL with campaign results and analytics."""
        try:
            # Prepare campaign update data
            update_data = {
                "contactId": client_id,
                "campaignData": {
                    "objective": campaign_data.get("objective"),
                    "platformsUsed": list(campaign_data.get("published_content", {}).keys()),
                    "publishedContent": campaign_data.get("published_content"),
                    "analytics": campaign_data.get("analytics_data"),
                    "status": campaign_data.get("status"),
                    "timestamp": datetime.now().isoformat()
                }
            }
            
            # Create or update opportunity/campaign in GHL
            # This is a simplified example - adjust based on your GHL setup
            opportunity_data = {
                "title": f"Social Media Campaign - {client_id}",
                "status": "won" if campaign_data.get("status") == "completed" else "open",
                "source": "ContentSocialSwarm",
                "pipelineId": "default",  # Use your pipeline ID
                "locationId": self.settings.GHL_LOCATION_ID,
                "contactId": client_id,
                "customFields": [
                    {
                        "key": "campaign_objective",
                        "value": campaign_data.get("objective", "")
                    },
                    {
                        "key": "platforms_used",
                        "value": ", ".join(campaign_data.get("published_content", {}).keys())
                    }
                ]
            }
            
            # Post to GHL (simplified - adjust endpoint based on your needs)
            response = requests.post(
                f"{self.base_url}/opportunities/",
                headers=self.headers,
                json=opportunity_data
            )
            
            if response.status_code in [200, 201]:
                return {
                    "status": "success",
                    "ghl_opportunity_id": response.json().get("id"),
                    "updated_data": update_data
                }
            else:
                logger.error(f"GHL update failed: {response.text}")
                return {
                    "status": "failed",
                    "error": response.text
                }
                
        except Exception as e:
            logger.error(f"GHL campaign update failed: {str(e)}")
            return {
                "status": "failed",
                "error": str(e)
            }
            
    async def create_lead_from_engagement(self, engagement_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a lead in GHL from social media engagement."""
        try:
            lead_data = {
                "firstName": engagement_data.get("name", "Social Media Lead"),
                "email": engagement_data.get("email", ""),
                "phone": engagement_data.get("phone", ""),
                "source": f"{engagement_data.get('platform', 'Social Media')} Engagement",
                "locationId": self.settings.GHL_LOCATION_ID,
                "tags": ["social-media-lead", engagement_data.get("platform", "unknown")],
                "customFields": [
                    {
                        "key": "engagement_platform",
                        "value": engagement_data.get("platform", "")
                    },
                    {
                        "key": "engagement_type",
                        "value": engagement_data.get("type", "")
                    },
                    {
                        "key": "post_id",
                        "value": engagement_data.get("post_id", "")
                    }
                ]
            }
            
            response = requests.post(
                f"{self.base_url}/contacts/",
                headers=self.headers,
                json=lead_data
            )
            
            if response.status_code in [200, 201]:
                return {
                    "status": "success",
                    "contact_id": response.json().get("id"),
                    "lead_data": lead_data
                }
            else:
                logger.error(f"GHL lead creation failed: {response.text}")
                return {
                    "status": "failed",
                    "error": response.text
                }
                
        except Exception as e:
            logger.error(f"GHL lead creation failed: {str(e)}")
            return {
                "status": "failed",
                "error": str(e)
            }
            
    async def trigger_automation(self, contact_id: str, trigger_name: str) -> Dict[str, Any]:
        """Trigger a GHL automation for a contact."""
        try:
            trigger_data = {
                "contactId": contact_id,
                "triggerName": trigger_name
            }
            
            # Trigger automation endpoint
            response = requests.post(
                f"{self.base_url}/contacts/{contact_id}/campaigns/",
                headers=self.headers,
                json=trigger_data
            )
            
            if response.status_code in [200, 201]:
                return {
                    "status": "success",
                    "trigger": trigger_name,
                    "contact_id": contact_id
                }
            else:
                return {
                    "status": "failed",
                    "error": response.text
                }
                
        except Exception as e:
            logger.error(f"GHL automation trigger failed: {str(e)}")
            return {
                "status": "failed",
                "error": str(e)
            }
            
    async def get_contact_info(self, contact_id: str) -> Dict[str, Any]:
        """Get contact information from GHL."""
        try:
            response = requests.get(
                f"{self.base_url}/contacts/{contact_id}",
                headers=self.headers
            )
            
            if response.status_code == 200:
                return {
                    "status": "success",
                    "contact_data": response.json()
                }
            else:
                return {
                    "status": "failed",
                    "error": response.text
                }
                
        except Exception as e:
            logger.error(f"GHL contact fetch failed: {str(e)}")
            return {
                "status": "failed",
                "error": str(e)
            } 