"""
Unified Vector Memory System for the AI Agent.
Stores Chat History, Documents, and Insights as embeddings for semantic retrieval.
"""

import time
import uuid
import logging
from typing import List, Dict, Any, Optional

from backend.embeddings import get_embedding_service
from backend.endee_vector_db import get_endee_client

logger = logging.getLogger(__name__)

class VectorMemoryManager:
    def __init__(self):
        self.embedder = get_embedding_service()
        self.collection_name = "agent_memory"
    
    async def _get_db(self):
        db = await get_endee_client()
        # Ensure collection exists
        await db.create_collection(self.collection_name, dimension=self.embedder.dimension)
        return db

    async def save_memory(self, text: str, memory_type: str, metadata: dict = None) -> str:
        """
        Embeds and saves a piece of knowledge into the Vector DB.
        memory_type can be: 'chat', 'document', 'insight'
        """
        if not text.strip():
            return ""
            
        try:
            db = await self._get_db()
            vector = self.embedder.generate_embedding(text)
            vector_id = str(uuid.uuid4())
            
            full_metadata = metadata or {}
            full_metadata["memory_type"] = memory_type
            full_metadata["timestamp"] = time.time()
            
            await db.upsert_vector(
                vector_id=vector_id,
                embedding=vector,
                metadata=full_metadata,
                text=text
            )
            logger.info(f"Saved {memory_type} to Vector Memory: {vector_id}")
            return vector_id
        except Exception as e:
            logger.error(f"Failed to save to vector memory: {e}")
            return ""

    async def retrieve_context(self, query: str, memory_type: Optional[str] = None, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieves relevant memory chunks based on semantic similarity.
        """
        try:
            db = await self._get_db()
            query_vector = self.embedder.generate_embedding(query)
            
            filters = {"memory_type": memory_type} if memory_type else None
            
            results = await db.search(
                query_embedding=query_vector,
                top_k=top_k,
                min_score=0.3, # Configurable threshold
                metadata_filter=filters
            )
            
            return [{"text": r.text, "score": r.score, "metadata": r.metadata} for r in results]
        except Exception as e:
            logger.error(f"Failed to retrieve from vector memory: {e}")
            return []

vector_memory_manager = VectorMemoryManager()