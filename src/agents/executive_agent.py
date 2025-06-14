"""
Executive Agent - Main orchestrator for ContentSocialSwarm.

This agent coordinates all platform agents, manages client workflows,
integrates with GoHighLevel CRM, and handles high-level decision making.
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, TypedDict

from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage

from src.agents.platform_agents.facebook_agent import FacebookAgent
from src.agents.platform_agents.instagram_agent import InstagramAgent
from src.agents.platform_agents.tiktok_agent import TikTokAgent
from src.agents.platform_agents.twitter_agent import TwitterAgent
from src.agents.platform_agents.ghl_agent import GHLAgent
from src.agents.content_factory import ContentFactory
from src.agents.analytics_agent import AnalyticsAgent
from src.config.settings import get_settings
from src.memory.vector_store import VectorStoreManager

logger = logging.getLogger(__name__)
settings = get_settings()


class ExecutiveState(TypedDict):
    """State structure for the Executive Agent."""
    client_id: str
    campaign_id: Optional[str]
    objective: str
    content_brief: str
    target_platforms: List[str]
    generated_content: Dict[str, Any]
    published_content: Dict[str, Any]
    analytics_data: Dict[str, Any]
    ghl_data: Dict[str, Any]
    error_messages: List[str]
    status: str
    created_at: datetime
    updated_at: datetime


class ExecutiveAgent:
    """Main orchestrator agent for ContentSocialSwarm."""
    
    def __init__(self, vector_store: VectorStoreManager):
        self.vector_store = vector_store
        self.settings = get_settings()
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.7
        )
        
        # Initialize platform agents
        self.facebook_agent = FacebookAgent()
        self.instagram_agent = InstagramAgent()
        self.tiktok_agent = TikTokAgent()
        self.twitter_agent = TwitterAgent()
        self.ghl_agent = GHLAgent()
        
        # Initialize specialized agents
        self.content_factory = ContentFactory(self.llm, self.vector_store)
        self.analytics_agent = AnalyticsAgent()
        
        # Initialize LangGraph workflow
        self.workflow = self._build_workflow()
        
        logger.info("Executive Agent initialized")
    
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow for content management."""
        workflow = StateGraph(ExecutiveState)
        
        # Add nodes
        workflow.add_node("analyze_brief", self._analyze_brief)
        workflow.add_node("generate_content", self._generate_content)
        workflow.add_node("finalize", self._finalize)
        
        # Define workflow edges
        workflow.set_entry_point("analyze_brief")
        workflow.add_edge("analyze_brief", "generate_content")
        workflow.add_edge("generate_content", "finalize")
        workflow.add_edge("finalize", END)
        
        return workflow.compile()
    
    async def initialize(self):
        """Initialize the Executive Agent and all sub-agents."""
        logger.info("Initializing Executive Agent...")
        
        # Initialize all platform agents
        await asyncio.gather(
            self.facebook_agent.initialize(),
            self.instagram_agent.initialize(),
            self.tiktok_agent.initialize(),
            self.twitter_agent.initialize(),
            self.ghl_agent.initialize(),
            self.content_factory.initialize(),
            self.analytics_agent.initialize()
        )
        
        logger.info("Executive Agent initialization complete")
    
    async def shutdown(self):
        """Shutdown the Executive Agent and cleanup resources."""
        logger.info("Shutting down Executive Agent...")
        
        # Shutdown all platform agents
        await asyncio.gather(
            self.facebook_agent.shutdown(),
            self.instagram_agent.shutdown(),
            self.tiktok_agent.shutdown(),
            self.twitter_agent.shutdown(),
            self.ghl_agent.shutdown(),
            self.content_factory.shutdown(),
            self.analytics_agent.shutdown(),
            return_exceptions=True
        )
        
        logger.info("Executive Agent shutdown complete")
    
    async def execute_campaign(
        self,
        client_id: str,
        objective: str,
        content_brief: str,
        target_platforms: List[str],
        campaign_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Execute a complete content campaign."""
        
        # Initialize state
        initial_state = ExecutiveState(
            client_id=client_id,
            campaign_id=campaign_id,
            objective=objective,
            content_brief=content_brief,
            target_platforms=target_platforms,
            generated_content={},
            published_content={},
            analytics_data={},
            ghl_data={},
            error_messages=[],
            status="started",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        try:
            # Execute workflow
            result = await self.workflow.ainvoke(initial_state)
            logger.info(f"Campaign executed successfully for client {client_id}")
            return result
            
        except Exception as e:
            logger.error(f"Campaign execution failed for client {client_id}: {str(e)}")
            raise
    
    async def _analyze_brief(self, state: ExecutiveState) -> ExecutiveState:
        """Analyze the content brief."""
        state["status"] = "brief_analyzed"
        state["updated_at"] = datetime.now()
        return state
    
    async def _generate_content(self, state: ExecutiveState) -> ExecutiveState:
        """Generate content."""
        state["status"] = "content_generated"
        state["updated_at"] = datetime.now()
        return state
    
    async def _finalize(self, state: ExecutiveState) -> ExecutiveState:
        """Finalize the campaign."""
        state["status"] = "completed"
        state["updated_at"] = datetime.now()
        return state 