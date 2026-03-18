"""
OpenAI Embeddings Module
Generates embeddings using OpenAI's text-embedding-3-small model.
"""

import logging
import os
from typing import List, Optional
from functools import lru_cache
import asyncio

from openai import AsyncOpenAI, OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)


class OpenAIEmbeddingService:
    """Service for generating embeddings using OpenAI.
    
    Uses the text-embedding-3-small model which provides:
    - 1536-dimensional embeddings
    - High performance (best value model)
    - Semantic understanding
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = "text-embedding-3-small"):
        """Initialize OpenAI embedding service.
        
        Args:
            api_key: OpenAI API key (from env if not provided)
            model: Embedding model to use (text-embedding-3-small or text-embedding-3-large)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        
        self.model = model
        self.client = OpenAI(api_key=self.api_key)
        self.async_client = AsyncOpenAI(api_key=self.api_key)
        self.embedding_dimension = 1536 if model == "text-embedding-3-small" else 3072
        
        logger.info(f"OpenAI Embedding Service initialized with model: {model}")
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def embed_text(self, text: str) -> List[float]:
        """Generate embedding for a single text.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector (list of floats)
        """
        try:
            # Remove excessive whitespace
            text = " ".join(text.split())
            
            response = self.client.embeddings.create(
                input=text,
                model=self.model
            )
            
            embedding = response.data[0].embedding
            logger.debug(f"Generated embedding for text (length: {len(text)})")
            
            return embedding
        
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            raise
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def embed_texts(self, texts: List[str], batch_size: int = 100) -> List[List[float]]:
        """Generate embeddings for multiple texts.
        
        Args:
            texts: List of texts to embed
            batch_size: Number of texts to process per API call
            
        Returns:
            List of embedding vectors
        """
        try:
            embeddings = []
            
            # Process in batches to optimize API calls
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                
                # Clean texts
                cleaned_batch = [" ".join(t.split()) for t in batch]
                
                response = self.client.embeddings.create(
                    input=cleaned_batch,
                    model=self.model
                )
                
                # Sort by index to maintain order
                batch_embeddings = sorted(
                    response.data,
                    key=lambda x: x.index
                )
                
                embeddings.extend([item.embedding for item in batch_embeddings])
                logger.info(f"Generated embeddings for batch {i // batch_size + 1} ({len(batch)} texts)")
            
            return embeddings
        
        except Exception as e:
            logger.error(f"Error generating batch embeddings: {str(e)}")
            raise
    
    async def embed_text_async(self, text: str) -> List[float]:
        """Generate embedding asynchronously.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        try:
            text = " ".join(text.split())
            
            response = await self.async_client.embeddings.create(
                input=text,
                model=self.model
            )
            
            return response.data[0].embedding
        
        except Exception as e:
            logger.error(f"Error in async embedding: {str(e)}")
            raise
    
    async def embed_texts_async(
        self,
        texts: List[str],
        batch_size: int = 100
    ) -> List[List[float]]:
        """Generate embeddings for multiple texts asynchronously.
        
        Args:
            texts: List of texts to embed
            batch_size: Batch size for API calls
            
        Returns:
            List of embedding vectors
        """
        try:
            embeddings = []
            tasks = []
            
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                cleaned_batch = [" ".join(t.split()) for t in batch]
                
                task = self.async_client.embeddings.create(
                    input=cleaned_batch,
                    model=self.model
                )
                tasks.append(task)
            
            responses = await asyncio.gather(*tasks)
            
            for response in responses:
                batch_embeddings = sorted(
                    response.data,
                    key=lambda x: x.index
                )
                embeddings.extend([item.embedding for item in batch_embeddings])
            
            logger.info(f"Generated {len(embeddings)} async embeddings")
            return embeddings
        
        except Exception as e:
            logger.error(f"Error in batch async embedding: {str(e)}")
            raise
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of generated embeddings.
        
        Returns:
            Embedding dimension (1536 for small, 3072 for large)
        """
        return self.embedding_dimension


# Global instance
_embedding_service: Optional[OpenAIEmbeddingService] = None


def get_embedding_service(
    api_key: Optional[str] = None,
    model: str = "text-embedding-3-small"
) -> OpenAIEmbeddingService:
    """Get or create embedding service instance.
    
    Args:
        api_key: OpenAI API key
        model: Embedding model
        
    Returns:
        OpenAIEmbeddingService instance
    """
    global _embedding_service
    
    if _embedding_service is None:
        _embedding_service = OpenAIEmbeddingService(api_key=api_key, model=model)
    
    return _embedding_service
