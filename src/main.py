"""
Main application entry point for ContentSocialSwarm.

This module initializes the FastAPI application, sets up routing,
and starts the LangGraph agent orchestration system.
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from src.agents.executive_agent import ExecutiveAgent
from src.config.settings import get_settings
from src.memory.vector_store import VectorStoreManager
from src.ui.routes import api_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Global settings
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info("Starting ContentSocialSwarm application...")
    
    # Initialize vector store
    vector_store = VectorStoreManager()
    await vector_store.initialize()
    app.state.vector_store = vector_store
    
    # Initialize Executive Agent
    executive_agent = ExecutiveAgent(vector_store=vector_store)
    await executive_agent.initialize()
    app.state.executive_agent = executive_agent
    
    logger.info("Application startup complete.")
    yield
    
    # Cleanup
    logger.info("Shutting down ContentSocialSwarm application...")
    await executive_agent.shutdown()
    await vector_store.close()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="ContentSocialSwarm",
        description="Marketing Agency Social Media Management System",
        version="1.0.0",
        lifespan=lifespan
    )
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include API routes
    app.include_router(api_router, prefix="/api/v1")
    
    # Static files
    static_dir = Path(__file__).parent / "ui" / "static"
    if static_dir.exists():
        app.mount("/static", StaticFiles(directory=static_dir), name="static")
    
    @app.get("/")
    async def root():
        return {
            "message": "ContentSocialSwarm API",
            "version": "1.0.0",
            "status": "running"
        }
    
    @app.get("/health")
    async def health_check():
        return {"status": "healthy", "timestamp": asyncio.get_event_loop().time()}
    
    return app


def main():
    """Main entry point."""
    app = create_app()
    
    # Run the application
    uvicorn.run(
        app,
        host=settings.HOST,
        port=settings.PORT,
        log_level="info",
        reload=settings.DEBUG
    )


if __name__ == "__main__":
    main() 