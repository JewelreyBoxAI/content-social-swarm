"""
Vector Store Manager for ContentSocialSwarm.

Handles vector storage and retrieval for content, analytics, and memory
using FAISS and ChromaDB for efficient similarity search.
"""

import logging
import os
from typing import Any, Dict, List, Optional
import asyncio
from datetime import datetime
import json

import chromadb
from chromadb.config import Settings
import numpy as np
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)


class VectorStoreManager:
    """Manages vector storage and retrieval for content and analytics."""
    
    def __init__(self, storage_path: str = "./data/vectorstore"):
        self.storage_path = storage_path
        self.client = None
        self.collection = None
        self.encoder = None
        
        # Ensure storage directory exists
        os.makedirs(storage_path, exist_ok=True)
        
    async def initialize(self):
        """Initialize the vector store and embedding model."""
        try:
            # Initialize ChromaDB client
            self.client = chromadb.PersistentClient(
                path=self.storage_path,
                settings=Settings(
                    anonymized_telemetry=False,
                    is_persistent=True
                )
            )
            
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name="contentsocialswarm",
                metadata={"description": "ContentSocialSwarm vector store"}
            )
            
            # Initialize sentence transformer
            self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
            
            logger.info("Vector store initialized successfully")
            
        except Exception as e:
            logger.error(f"Vector store initialization failed: {str(e)}")
            raise
    
    async def close(self):
        """Close the vector store connections."""
        self.client = None
        self.collection = None
        self.encoder = None
        logger.info("Vector store closed")
    
    async def store_content(
        self,
        content: str,
        metadata: Dict[str, Any],
        content_id: Optional[str] = None
    ) -> str:
        """Store content with metadata in the vector store."""
        try:
            if not self.collection or not self.encoder:
                raise Exception("Vector store not initialized")
            
            # Generate embedding
            embedding = self.encoder.encode(content).tolist()
            
            # Generate ID if not provided
            if not content_id:
                content_id = f"{metadata.get('type', 'content')}_{hash(content) % 100000}_{int(datetime.now().timestamp())}"
            
            # Prepare metadata
            store_metadata = {
                **metadata,
                "stored_at": datetime.now().isoformat(),
                "content_length": len(content)
            }
            
            # Store in ChromaDB
            self.collection.add(
                embeddings=[embedding],
                documents=[content],
                metadatas=[store_metadata],
                ids=[content_id]
            )
            
            logger.debug(f"Content stored with ID: {content_id}")
            return content_id
            
        except Exception as e:
            logger.error(f"Content storage failed: {str(e)}")
            raise
    
    async def search_similar_content(
        self,
        query: str,
        limit: int = 10,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Search for similar content in the vector store."""
        try:
            if not self.collection or not self.encoder:
                raise Exception("Vector store not initialized")
            
            # Generate query embedding
            query_embedding = self.encoder.encode(query).tolist()
            
            # Prepare where clause for filtering
            where_clause = filter_metadata if filter_metadata else None
            
            # Search similar content
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=limit,
                where=where_clause,
                include=["documents", "metadatas", "distances"]
            )
            
            # Format results
            similar_content = []
            for i in range(len(results['documents'][0])):
                similar_content.append({
                    "content": results['documents'][0][i],
                    "metadata": results['metadatas'][0][i],
                    "similarity_score": 1 - results['distances'][0][i],  # Convert distance to similarity
                    "id": results['ids'][0][i] if 'ids' in results else None
                })
            
            return similar_content
            
        except Exception as e:
            logger.error(f"Content search failed: {str(e)}")
            return []
    
    async def get_content_by_id(self, content_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve specific content by ID."""
        try:
            if not self.collection:
                raise Exception("Vector store not initialized")
            
            results = self.collection.get(
                ids=[content_id],
                include=["documents", "metadatas"]
            )
            
            if results['documents']:
                return {
                    "content": results['documents'][0],
                    "metadata": results['metadatas'][0],
                    "id": content_id
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Content retrieval failed: {str(e)}")
            return None
    
    async def delete_content(self, content_id: str) -> bool:
        """Delete content from the vector store."""
        try:
            if not self.collection:
                raise Exception("Vector store not initialized")
            
            self.collection.delete(ids=[content_id])
            logger.debug(f"Content deleted: {content_id}")
            return True
            
        except Exception as e:
            logger.error(f"Content deletion failed: {str(e)}")
            return False
    
    async def get_analytics_insights(self, client_id: str, days: int = 30) -> Dict[str, Any]:
        """Get analytics insights for a specific client."""
        try:
            # Search for analytics data for the client
            analytics_content = await self.search_similar_content(
                query=f"analytics client {client_id}",
                limit=100,
                filter_metadata={"type": "analytics", "client_id": client_id}
            )
            
            if not analytics_content:
                return {"message": "No analytics data found", "client_id": client_id}
            
            # Aggregate insights (simplified example)
            total_posts = len([c for c in analytics_content if c['metadata'].get('type') == 'analytics'])
            avg_engagement = sum([
                c['metadata'].get('engagement_rate', 0) 
                for c in analytics_content 
                if 'engagement_rate' in c['metadata']
            ]) / max(1, len([c for c in analytics_content if 'engagement_rate' in c['metadata']]))
            
            return {
                "client_id": client_id,
                "period_days": days,
                "total_posts_analyzed": total_posts,
                "average_engagement_rate": avg_engagement,
                "insights_available": len(analytics_content)
            }
            
        except Exception as e:
            logger.error(f"Analytics insights failed: {str(e)}")
            return {"error": str(e), "client_id": client_id}
    
    async def store_campaign_memory(
        self,
        campaign_id: str,
        client_id: str,
        campaign_data: Dict[str, Any]
    ) -> str:
        """Store campaign data as memory for future reference."""
        try:
            memory_content = f"""
            Campaign Memory for Client {client_id}:
            
            Objective: {campaign_data.get('objective', 'N/A')}
            Platforms: {', '.join(campaign_data.get('target_platforms', []))}
            Status: {campaign_data.get('status', 'N/A')}
            
            Generated Content Summary:
            {json.dumps(campaign_data.get('generated_content', {}), indent=2)}
            
            Published Results:
            {json.dumps(campaign_data.get('published_content', {}), indent=2)}
            
            Analytics Data:
            {json.dumps(campaign_data.get('analytics_data', {}), indent=2)}
            """
            
            metadata = {
                "type": "campaign_memory",
                "campaign_id": campaign_id,
                "client_id": client_id,
                "status": campaign_data.get('status', 'unknown'),
                "platforms": campaign_data.get('target_platforms', []),
                "timestamp": datetime.now().isoformat()
            }
            
            memory_id = await self.store_content(
                content=memory_content,
                metadata=metadata,
                content_id=f"campaign_{campaign_id}"
            )
            
            return memory_id
            
        except Exception as e:
            logger.error(f"Campaign memory storage failed: {str(e)}")
            raise 