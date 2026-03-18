"""Embedding generation using SentenceTransformers."""
from typing import List
from sentence_transformers import SentenceTransformer
from backend.config import settings
from backend.logging_config import get_logger

logger = get_logger("embeddings")


class EmbeddingService:
    """Service for generating embeddings using SentenceTransformers."""
    
    def __init__(self):
        """Initialize the embedding service."""
        logger.info(f"Loading embedding model: {settings.embedding_model}")
        self.model = SentenceTransformer(settings.embedding_model)
        self.dimension = settings.embedding_dimension
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text.
        
        Args:
            text: The text to embed.
            
        Returns:
            A list of floats representing the embedding vector.
        """
        try:
            embedding = self.model.encode(text, convert_to_numpy=False)
            return embedding.tolist() if hasattr(embedding, 'tolist') else embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            raise
    
    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts.
        
        Args:
            texts: List of texts to embed.
            
        Returns:
            List of embedding vectors.
        """
        try:
            embeddings = self.model.encode(texts, convert_to_numpy=False)
            return [
                e.tolist() if hasattr(e, 'tolist') else e 
                for e in embeddings
            ]
        except Exception as e:
            logger.error(f"Error generating batch embeddings: {str(e)}")
            raise


# Global embedding service instance
_embedding_service = None


def get_embedding_service() -> EmbeddingService:
    """Get or create the embedding service singleton."""
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service
