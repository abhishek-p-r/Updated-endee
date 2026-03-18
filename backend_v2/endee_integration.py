"""
Endee Vector Database Integration Module
Handles all interactions with Endee vector database for storing and retrieving embeddings.
"""

import logging
import asyncio
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import json
import os

import httpx
import numpy as np
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)


@dataclass
class VectorMetadata:
    """Metadata associated with a vector in Endee."""
    document_id: str
    chunk_id: str
    text: str
    source: str
    chunk_index: int
    total_chunks: int
    created_at: str
    updated_at: str
    metadata: Dict[str, Any]


@dataclass
class SearchResult:
    """Result from Endee semantic search."""
    id: str
    score: float
    text: str
    metadata: VectorMetadata
    embedding: Optional[List[float]] = None


class EndeeVectorDB:
    """
    Endee Vector Database client for semantic search and storage.
    
    Handles:
    - Connection to Endee server
    - Storing embeddings with metadata
    - Semantic similarity search
    - Vector retrieval and management
    """
    
    def __init__(
        self,
        endee_url: str = "http://localhost:6379",
        db_name: str = "knowledge_base",
        vector_dimension: int = 1536,  # OpenAI embedding dimension
        timeout: float = 30.0
    ):
        """Initialize Endee Vector DB client.
        
        Args:
            endee_url: URL of Endee server
            db_name: Database/collection name
            vector_dimension: Dimension of embeddings (1536 for OpenAI)
            timeout: Request timeout in seconds
        """
        self.endee_url = endee_url
        self.db_name = db_name
        self.vector_dimension = vector_dimension
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout)
        self.is_connected = False
        
        logger.info(f"Initializing Endee Vector DB at {endee_url}")
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def health_check(self) -> bool:
        """Check if Endee server is running and healthy.
        
        Returns:
            True if server is healthy, False otherwise.
        """
        try:
            response = await self.client.get(
                f"{self.endee_url}/health",
                timeout=self.timeout
            )
            self.is_connected = response.status_code == 200
            logger.info(f"Endee health check: {'✓ Connected' if self.is_connected else '✗ Disconnected'}")
            return self.is_connected
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            self.is_connected = False
            return False
    
    async def create_collection(self) -> bool:
        """Create a collection in Endee if it doesn't exist.
        
        Returns:
            True if successful, False otherwise.
        """
        try:
            payload = {
                "name": self.db_name,
                "dimension": self.vector_dimension,
                "metric": "cosine"  # Cosine similarity for semantic search
            }
            
            response = await self.client.post(
                f"{self.endee_url}/collections",
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code in [200, 201, 409]:  # 409 = already exists
                logger.info(f"Collection '{self.db_name}' ready")
                return True
            
            logger.error(f"Failed to create collection: {response.text}")
            return False
        
        except Exception as e:
            logger.error(f"Error creating collection: {str(e)}")
            return False
    
    async def store_vectors(
        self,
        vectors: List[Tuple[str, List[float], VectorMetadata]]
    ) -> bool:
        """Store embeddings with metadata in Endee.
        
        Args:
            vectors: List of (id, embedding, metadata) tuples
            
        Returns:
            True if successful, False otherwise.
        """
        try:
            payloads = []
            
            for vector_id, embedding, metadata in vectors:
                payload = {
                    "id": vector_id,
                    "vector": embedding,
                    "metadata": {
                        "document_id": metadata.document_id,
                        "chunk_id": metadata.chunk_id,
                        "text": metadata.text,
                        "source": metadata.source,
                        "chunk_index": metadata.chunk_index,
                        "total_chunks": metadata.total_chunks,
                        "created_at": metadata.created_at,
                        "updated_at": metadata.updated_at,
                        **metadata.metadata
                    }
                }
                payloads.append(payload)
            
            response = await self.client.post(
                f"{self.endee_url}/collections/{self.db_name}/upsert",
                json={"vectors": payloads},
                timeout=self.timeout
            )
            
            if response.status_code in [200, 201]:
                logger.info(f"Stored {len(vectors)} vectors in Endee")
                return True
            
            logger.error(f"Failed to store vectors: {response.text}")
            return False
        
        except Exception as e:
            logger.error(f"Error storing vectors: {str(e)}")
            return False
    
    async def semantic_search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        score_threshold: float = 0.5
    ) -> List[SearchResult]:
        """Perform semantic similarity search in Endee.
        
        Args:
            query_embedding: Query vector (from OpenAI embeddings)
            top_k: Number of top results to return
            score_threshold: Minimum similarity score (0-1)
            
        Returns:
            List of SearchResult objects sorted by relevance.
        """
        try:
            payload = {
                "vector": query_embedding,
                "top_k": top_k,
                "threshold": score_threshold
            }
            
            response = await self.client.post(
                f"{self.endee_url}/collections/{self.db_name}/search",
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code != 200:
                logger.error(f"Search failed: {response.text}")
                return []
            
            results = response.json().get("results", [])
            search_results = []
            
            for result in results:
                metadata_dict = result.get("metadata", {})
                
                metadata = VectorMetadata(
                    document_id=metadata_dict.get("document_id", ""),
                    chunk_id=metadata_dict.get("chunk_id", ""),
                    text=metadata_dict.get("text", ""),
                    source=metadata_dict.get("source", ""),
                    chunk_index=metadata_dict.get("chunk_index", 0),
                    total_chunks=metadata_dict.get("total_chunks", 0),
                    created_at=metadata_dict.get("created_at", ""),
                    updated_at=metadata_dict.get("updated_at", ""),
                    metadata={k: v for k, v in metadata_dict.items() 
                             if k not in ["document_id", "chunk_id", "text", "source", 
                                         "chunk_index", "total_chunks", "created_at", "updated_at"]}
                )
                
                search_result = SearchResult(
                    id=result.get("id", ""),
                    score=float(result.get("score", 0)),
                    text=metadata.text,
                    metadata=metadata,
                    embedding=result.get("vector", None)
                )
                search_results.append(search_result)
            
            logger.info(f"Found {len(search_results)} relevant chunks")
            return search_results
        
        except Exception as e:
            logger.error(f"Error performing search: {str(e)}")
            return []
    
    async def delete_collection(self) -> bool:
        """Delete the collection from Endee.
        
        Returns:
            True if successful, False otherwise.
        """
        try:
            response = await self.client.delete(
                f"{self.endee_url}/collections/{self.db_name}",
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                logger.info(f"Collection '{self.db_name}' deleted")
                return True
            
            logger.error(f"Failed to delete collection: {response.text}")
            return False
        
        except Exception as e:
            logger.error(f"Error deleting collection: {str(e)}")
            return False
    
    async def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the collection.
        
        Returns:
            Dictionary with collection statistics.
        """
        try:
            response = await self.client.get(
                f"{self.endee_url}/collections/{self.db_name}/stats",
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                stats = response.json()
                logger.info(f"Collection stats: {stats}")
                return stats
            
            return {}
        
        except Exception as e:
            logger.error(f"Error getting collection stats: {str(e)}")
            return {}
    
    async def close(self):
        """Close the HTTP client connection."""
        await self.client.aclose()
        logger.info("Endee client closed")


# Global instance
_endee_client: Optional[EndeeVectorDB] = None


async def get_endee_client(
    endee_url: Optional[str] = None,
    db_name: str = "knowledge_base"
) -> EndeeVectorDB:
    """Get or create Endee client instance.
    
    Args:
        endee_url: Endee server URL (from env if not provided)
        db_name: Database name
        
    Returns:
        EndeeVectorDB instance
    """
    global _endee_client
    
    if _endee_client is None:
        url = endee_url or os.getenv("ENDEE_URL", "http://localhost:6379")
        _endee_client = EndeeVectorDB(
            endee_url=url,
            db_name=db_name,
            vector_dimension=1536  # OpenAI embedding dimension
        )
        await _endee_client.health_check()
    
    return _endee_client
