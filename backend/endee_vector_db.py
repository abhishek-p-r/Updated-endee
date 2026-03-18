"""
Endee Vector Database Integration Module

This module provides a complete wrapper around the Endee vector database
for storing, retrieving, and managing embeddings efficiently.
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import httpx
import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class VectorRecord:
    """Represents a single vector record in Endee."""
    id: str
    vector: List[float]
    metadata: Dict[str, Any]
    text: str = ""
    
    def to_dict(self) -> Dict:
        """Convert record to dictionary."""
        return asdict(self)


@dataclass
class SearchResult:
    """Represents a search result from Endee."""
    id: str
    score: float
    metadata: Dict[str, Any]
    text: str
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "score": self.score,
            "metadata": self.metadata,
            "text": self.text
        }


class EndeeVectorDB:
    """
    Complete Endee Vector Database client for embeddings management.
    
    Features:
    - Store embeddings with metadata
    - Semantic search using vector similarity
    - Batch operations
    - Document management
    - Health checks
    """
    
    def __init__(self, host: str = "localhost", port: int = 8000):
        """
        Initialize Endee vector database client.
        
        Args:
            host: Endee server host (default: localhost)
            port: Endee server port (default: 8000)
        """
        self.host = host
        self.port = port
        self.base_url = f"http://{host}:{port}"
        self.client = httpx.AsyncClient(base_url=self.base_url, timeout=30.0)
        self.collection_name = "documents"
        
        logger.info(f"Initialized Endee Vector DB client at {self.base_url}")
    
    async def health_check(self) -> bool:
        """
        Check if Endee server is healthy.
        
        Returns:
            True if healthy, False otherwise.
        """
        try:
            response = await self.client.get("/health")
            is_healthy = response.status_code == 200
            logger.info(f"Endee health check: {'✓ Healthy' if is_healthy else '✗ Unhealthy'}")
            return is_healthy
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return False
    
    async def create_collection(self, collection_name: str, dimension: int = 1536) -> bool:
        """
        Create a new collection in Endee.
        
        Args:
            collection_name: Name of the collection
            dimension: Vector dimension size (default: 1536 for OpenAI embeddings)
            
        Returns:
            True if successful, False otherwise.
        """
        try:
            payload = {
                "name": collection_name,
                "dimension": dimension,
                "description": "Vector storage for document embeddings"
            }
            response = await self.client.post(
                "/collections",
                json=payload
            )
            
            if response.status_code in [200, 201]:
                self.collection_name = collection_name
                logger.info(f"Created collection: {collection_name}")
                return True
            else:
                logger.warning(f"Collection creation returned status {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error creating collection: {str(e)}")
            return False
    
    async def upsert_vector(
        self,
        vector_id: str,
        embedding: List[float],
        metadata: Dict[str, Any],
        text: str = ""
    ) -> bool:
        """
        Upsert (insert or update) a single vector.
        
        Args:
            vector_id: Unique identifier for the vector
            embedding: Vector embedding (list of floats)
            metadata: Associated metadata
            text: Original text content
            
        Returns:
            True if successful, False otherwise.
        """
        try:
            payload = {
                "id": vector_id,
                "values": embedding,
                "metadata": {
                    **metadata,
                    "text": text,
                    "text_length": len(text)
                }
            }
            
            response = await self.client.post(
                f"/collections/{self.collection_name}/vectors",
                json=payload
            )
            
            return response.status_code in [200, 201]
            
        except Exception as e:
            logger.error(f"Error upserting vector {vector_id}: {str(e)}")
            return False
    
    async def upsert_batch(
        self,
        vectors: List[Tuple[str, List[float], Dict[str, Any], str]]
    ) -> int:
        """
        Batch upsert multiple vectors efficiently.
        
        Args:
            vectors: List of (id, embedding, metadata, text) tuples
            
        Returns:
            Number of vectors successfully upserted.
        """
        try:
            payload = {
                "vectors": [
                    {
                        "id": vector_id,
                        "values": embedding,
                        "metadata": {
                            **metadata,
                            "text": text,
                            "text_length": len(text)
                        }
                    }
                    for vector_id, embedding, metadata, text in vectors
                ]
            }
            
            response = await self.client.post(
                f"/collections/{self.collection_name}/vectors/batch",
                json=payload
            )
            
            if response.status_code in [200, 201]:
                result = response.json()
                count = result.get("upserted", len(vectors))
                logger.info(f"Batch upserted {count} vectors")
                return count
            else:
                logger.error(f"Batch upsert failed with status {response.status_code}")
                return 0
                
        except Exception as e:
            logger.error(f"Error in batch upsert: {str(e)}")
            return 0
    
    async def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        min_score: float = 0.0,
        metadata_filter: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """
        Search for similar vectors in the database.
        
        Args:
            query_embedding: Query vector embedding
            top_k: Number of results to return
            min_score: Minimum similarity score threshold
            metadata_filter: Optional metadata filters
            
        Returns:
            List of SearchResult objects.
        """
        try:
            payload = {
                "vector": query_embedding,
                "top_k": top_k,
                "min_score": min_score
            }
            
            if metadata_filter:
                payload["filter"] = metadata_filter
            
            response = await self.client.post(
                f"/collections/{self.collection_name}/search",
                json=payload
            )
            
            if response.status_code != 200:
                logger.error(f"Search failed with status {response.status_code}")
                return []
            
            results_data = response.json()
            results = []
            
            for item in results_data.get("results", []):
                result = SearchResult(
                    id=item.get("id", ""),
                    score=item.get("score", 0.0),
                    metadata=item.get("metadata", {}),
                    text=item.get("metadata", {}).get("text", "")
                )
                results.append(result)
            
            logger.debug(f"Search returned {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Error searching vectors: {str(e)}")
            return []
    
    async def delete_vector(self, vector_id: str) -> bool:
        """
        Delete a vector by ID.
        
        Args:
            vector_id: ID of the vector to delete
            
        Returns:
            True if successful, False otherwise.
        """
        try:
            response = await self.client.delete(
                f"/collections/{self.collection_name}/vectors/{vector_id}"
            )
            return response.status_code in [200, 204]
            
        except Exception as e:
            logger.error(f"Error deleting vector {vector_id}: {str(e)}")
            return False
    
    async def get_vector(self, vector_id: str) -> Optional[VectorRecord]:
        """
        Retrieve a specific vector by ID.
        
        Args:
            vector_id: ID of the vector
            
        Returns:
            VectorRecord if found, None otherwise.
        """
        try:
            response = await self.client.get(
                f"/collections/{self.collection_name}/vectors/{vector_id}"
            )
            
            if response.status_code != 200:
                return None
            
            data = response.json()
            return VectorRecord(
                id=data.get("id", ""),
                vector=data.get("values", []),
                metadata=data.get("metadata", {}),
                text=data.get("metadata", {}).get("text", "")
            )
            
        except Exception as e:
            logger.error(f"Error getting vector {vector_id}: {str(e)}")
            return None
    
    async def list_vectors(self, limit: int = 100, offset: int = 0) -> List[VectorRecord]:
        """
        List vectors in the collection.
        
        Args:
            limit: Maximum number of results
            offset: Offset for pagination
            
        Returns:
            List of VectorRecord objects.
        """
        try:
            response = await self.client.get(
                f"/collections/{self.collection_name}/vectors",
                params={"limit": limit, "offset": offset}
            )
            
            if response.status_code != 200:
                return []
            
            data = response.json()
            records = []
            
            for item in data.get("vectors", []):
                record = VectorRecord(
                    id=item.get("id", ""),
                    vector=item.get("values", []),
                    metadata=item.get("metadata", {}),
                    text=item.get("metadata", {}).get("text", "")
                )
                records.append(record)
            
            return records
            
        except Exception as e:
            logger.error(f"Error listing vectors: {str(e)}")
            return []
    
    async def clear_collection(self) -> bool:
        """
        Clear all vectors from the collection.
        
        Returns:
            True if successful, False otherwise.
        """
        try:
            response = await self.client.delete(
                f"/collections/{self.collection_name}/vectors"
            )
            return response.status_code in [200, 204]
            
        except Exception as e:
            logger.error(f"Error clearing collection: {str(e)}")
            return False
    
    async def get_collection_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the collection.
        
        Returns:
            Collection statistics.
        """
        try:
            response = await self.client.get(
                f"/collections/{self.collection_name}/stats"
            )
            
            if response.status_code != 200:
                return {}
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Error getting collection stats: {str(e)}")
            return {}
    
    async def close(self):
        """Close the client connection."""
        await self.client.aclose()


# Singleton instance
_endee_client: Optional[EndeeVectorDB] = None


async def get_endee_client(
    host: str = "localhost",
    port: int = 8000
) -> EndeeVectorDB:
    """
    Get or create Endee vector database client singleton.
    
    Args:
        host: Endee server host
        port: Endee server port
        
    Returns:
        EndeeVectorDB client instance.
    """
    global _endee_client
    
    if _endee_client is None:
        _endee_client = EndeeVectorDB(host=host, port=port)
    
    return _endee_client
