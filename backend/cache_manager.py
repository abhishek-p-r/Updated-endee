"""Caching layer for query results and embeddings."""
import hashlib
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from backend.logging_config import get_logger

logger = get_logger("cache_manager")


class CacheEntry:
    """A single cache entry with TTL."""
    
    def __init__(self, data: Any, ttl_seconds: int = 3600):
        """Initialize cache entry.
        
        Args:
            data: The data to cache.
            ttl_seconds: Time to live in seconds.
        """
        self.data = data
        self.created_at = datetime.now()
        self.ttl_seconds = ttl_seconds
    
    def is_expired(self) -> bool:
        """Check if cache entry is expired.
        
        Returns:
            True if expired, False otherwise.
        """
        expiry = self.created_at + timedelta(seconds=self.ttl_seconds)
        return datetime.now() > expiry


class RAGCache:
    """In-memory cache for RAG system."""
    
    def __init__(self, default_ttl: int = 3600):
        """Initialize cache.
        
        Args:
            default_ttl: Default TTL for cache entries in seconds.
        """
        self.cache: Dict[str, CacheEntry] = {}
        self.default_ttl = default_ttl
        self.hit_count = 0
        self.miss_count = 0
    
    def _generate_key(self, query: str, filters: Optional[Dict] = None) -> str:
        """Generate cache key from query and filters.
        
        Args:
            query: The query text.
            filters: Optional filters to include in key.
            
        Returns:
            Cache key hash.
        """
        key_data = f"{query}:{json.dumps(filters or {}, sort_keys=True)}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get(
        self,
        query: str,
        filters: Optional[Dict] = None
    ) -> Optional[Any]:
        """Retrieve value from cache.
        
        Args:
            query: The query text.
            filters: Optional filters.
            
        Returns:
            Cached data or None if not found/expired.
        """
        key = self._generate_key(query, filters)
        
        if key in self.cache:
            entry = self.cache[key]
            
            if entry.is_expired():
                del self.cache[key]
                self.miss_count += 1
                logger.debug(f"Cache entry expired for key: {key}")
                return None
            
            self.hit_count += 1
            logger.debug(f"Cache hit for query: {query}")
            return entry.data
        
        self.miss_count += 1
        logger.debug(f"Cache miss for query: {query}")
        return None
    
    def set(
        self,
        query: str,
        data: Any,
        filters: Optional[Dict] = None,
        ttl: Optional[int] = None
    ) -> None:
        """Store value in cache.
        
        Args:
            query: The query text.
            data: Data to cache.
            filters: Optional filters.
            ttl: Optional TTL override in seconds.
        """
        key = self._generate_key(query, filters)
        ttl = ttl or self.default_ttl
        self.cache[key] = CacheEntry(data, ttl)
        logger.debug(f"Cache set for query: {query}, TTL: {ttl}s")
    
    def invalidate(self, query: str = None, filters: Optional[Dict] = None) -> None:
        """Invalidate cache entries.
        
        Args:
            query: Optional specific query to invalidate.
            filters: Optional filters for specific invalidation.
        """
        if query:
            key = self._generate_key(query, filters)
            if key in self.cache:
                del self.cache[key]
                logger.info(f"Cache invalidated for query: {query}")
        else:
            self.cache.clear()
            logger.info("Cache cleared completely")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics.
        
        Returns:
            Dictionary with cache stats.
        """
        total_requests = self.hit_count + self.miss_count
        hit_rate = (self.hit_count / total_requests * 100) if total_requests > 0 else 0
        
        return {
            "total_entries": len(self.cache),
            "hit_count": self.hit_count,
            "miss_count": self.miss_count,
            "total_requests": total_requests,
            "hit_rate_percent": hit_rate,
            "size_estimate": len(str(self.cache))
        }
    
    def cleanup_expired(self) -> int:
        """Remove all expired entries.
        
        Returns:
            Number of entries removed.
        """
        expired_keys = [
            key for key, entry in self.cache.items()
            if entry.is_expired()
        ]
        
        for key in expired_keys:
            del self.cache[key]
        
        if expired_keys:
            logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")
        
        return len(expired_keys)


class EmbeddingCache:
    """Dedicated cache for document embeddings."""
    
    def __init__(self, default_ttl: int = 86400):  # 24 hours
        """Initialize embedding cache.
        
        Args:
            default_ttl: Default TTL for embeddings in seconds.
        """
        self.embeddings: Dict[str, CacheEntry] = {}
        self.default_ttl = default_ttl
    
    def get_embedding(self, text: str) -> Optional[List[float]]:
        """Get cached embedding.
        
        Args:
            text: The text to look up.
            
        Returns:
            Cached embedding or None.
        """
        key = hashlib.md5(text.encode()).hexdigest()
        
        if key in self.embeddings:
            entry = self.embeddings[key]
            if not entry.is_expired():
                return entry.data
            else:
                del self.embeddings[key]
        
        return None
    
    def cache_embedding(self, text: str, embedding: List[float]) -> None:
        """Cache an embedding.
        
        Args:
            text: The text that was embedded.
            embedding: The embedding vector.
        """
        key = hashlib.md5(text.encode()).hexdigest()
        self.embeddings[key] = CacheEntry(embedding, self.default_ttl)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get embedding cache statistics.
        
        Returns:
            Cache statistics.
        """
        return {
            "cached_embeddings": len(self.embeddings),
            "memory_usage_estimate": len(str(self.embeddings))
        }


# Global cache instances
_query_cache = None
_embedding_cache = None


def get_query_cache() -> RAGCache:
    """Get or create the query cache singleton."""
    global _query_cache
    if _query_cache is None:
        _query_cache = RAGCache(default_ttl=3600)  # 1 hour for queries
    return _query_cache


def get_embedding_cache() -> EmbeddingCache:
    """Get or create the embedding cache singleton."""
    global _embedding_cache
    if _embedding_cache is None:
        _embedding_cache = EmbeddingCache(default_ttl=86400)  # 24 hours
    return _embedding_cache
