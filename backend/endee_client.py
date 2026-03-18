"""Client for interacting with Endee vector database."""
import httpx
import json
from typing import List, Dict, Any, Optional
from backend.config import settings
from backend.logging_config import get_logger

logger = get_logger("endee_client")


class EndeeClient:
    """HTTP client for Endee vector database."""
    
    def __init__(self, base_url: str = None):
        """Initialize the Endee client.
        
        Args:
            base_url: The base URL for the Endee server.
        """
        self.base_url = base_url or settings.endee_url
        self.collection_name = settings.endee_collection_name
        logger.info(f"Initialized Endee client with base URL: {self.base_url}")
    
    async def health_check(self) -> bool:
        """Check if Endee server is running.
        
        Returns:
            True if server is healthy, False otherwise.
        """
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(f"{self.base_url}/health")
                logger.info(f"Health check response: {response.status_code}")
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return False
    
    async def create_collection(self, dimension: int) -> bool:
        """Create a collection in Endee.
        
        Args:
            dimension: The dimension of the vectors.
            
        Returns:
            True if successful, False otherwise.
        """
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                payload = {
                    "name": self.collection_name,
                    "dimension": dimension,
                    "metric": "cosine"
                }
                response = await client.post(
                    f"{self.base_url}/collections",
                    json=payload
                )
                logger.info(f"Create collection response: {response.status_code}")
                return response.status_code in [200, 201]
        except Exception as e:
            logger.error(f"Failed to create collection: {str(e)}")
            return False
    
    async def upsert_vectors(
        self,
        vectors: List[Dict[str, Any]]
    ) -> bool:
        """Upsert vectors into the collection.
        
        Args:
            vectors: List of vector objects with id, vector, and metadata.
            
        Returns:
            True if successful, False otherwise.
        """
        try:
            async with httpx.AsyncClient(timeout=60) as client:
                payload = {
                    "collection": self.collection_name,
                    "vectors": vectors
                }
                response = await client.post(
                    f"{self.base_url}/upsert",
                    json=payload
                )
                logger.info(f"Upsert response: {response.status_code}")
                return response.status_code in [200, 201]
        except Exception as e:
            logger.error(f"Failed to upsert vectors: {str(e)}")
            return False
    
    async def search(
        self,
        query_vector: List[float],
        limit: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Search for similar vectors.
        
        Args:
            query_vector: The query embedding vector.
            limit: Maximum number of results to return.
            filters: Optional filters to apply.
            
        Returns:
            List of search results with metadata.
        """
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                payload = {
                    "collection": self.collection_name,
                    "vector": query_vector,
                    "limit": limit,
                    "with_payload": True
                }
                if filters:
                    payload["filter"] = filters
                
                response = await client.post(
                    f"{self.base_url}/search",
                    json=payload
                )
                
                if response.status_code == 200:
                    data = response.json()
                    logger.info(f"Search returned {len(data.get('results', []))} results")
                    return data.get('results', [])
                else:
                    logger.error(f"Search failed with status {response.status_code}")
                    return []
        except Exception as e:
            logger.error(f"Search error: {str(e)}")
            return []
    
    async def delete_collection(self) -> bool:
        """Delete the collection.
        
        Returns:
            True if successful, False otherwise.
        """
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.delete(
                    f"{self.base_url}/collections/{self.collection_name}"
                )
                logger.info(f"Delete collection response: {response.status_code}")
                return response.status_code in [200, 204]
        except Exception as e:
            logger.error(f"Failed to delete collection: {str(e)}")
            return False


# Global Endee client instance
_endee_client = None


async def get_endee_client() -> EndeeClient:
    """Get or create the Endee client singleton."""
    global _endee_client
    if _endee_client is None:
        _endee_client = EndeeClient()
    return _endee_client
