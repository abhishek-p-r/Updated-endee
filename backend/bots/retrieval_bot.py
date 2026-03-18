"""Knowledge Retrieval Bot - retrieves relevant documents from Endee."""
import asyncio
from typing import List, Dict, Any
from backend.embeddings import get_embedding_service
from backend.endee_client import get_endee_client
from backend.config import settings
from backend.logging_config import get_logger

logger = get_logger("retrieval_bot")


class KnowledgeRetrievalBot:
    """Bot responsible for retrieving relevant knowledge from Endee."""
    
    def __init__(self):
        """Initialize the retrieval bot."""
        self.embedding_service = get_embedding_service()
        logger.info("Initialized Knowledge Retrieval Bot")
    
    async def retrieve_knowledge(self, query: str) -> List[Dict[str, Any]]:
        """Retrieve relevant knowledge chunks for a query.
        
        Args:
            query: The search query.
            
        Returns:
            List of relevant knowledge chunks with metadata.
        """
        try:
            logger.info(f"Retrieving knowledge for: {query}")
            
            # Generate query embedding
            query_embedding = self.embedding_service.generate_embedding(query)
            
            # Search in Endee
            endee_client = await get_endee_client()
            results = await endee_client.search(
                query_vector=query_embedding,
                limit=settings.max_retrieved_documents
            )
            
            logger.info(f"Retrieved {len(results)} relevant documents")
            return results
        
        except Exception as e:
            logger.error(f"Error retrieving knowledge: {str(e)}")
            return []
    
    async def retrieve_with_filters(
        self,
        query: str,
        filters: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """Retrieve knowledge with optional filters.
        
        Args:
            query: The search query.
            filters: Optional filters to apply.
            
        Returns:
            Filtered search results.
        """
        try:
            # Generate query embedding
            query_embedding = self.embedding_service.generate_embedding(query)
            
            # Search with filters
            endee_client = await get_endee_client()
            results = await endee_client.search(
                query_vector=query_embedding,
                limit=settings.max_retrieved_documents,
                filters=filters
            )
            
            logger.info(f"Retrieved {len(results)} filtered documents")
            return results
        
        except Exception as e:
            logger.error(f"Error retrieving filtered knowledge: {str(e)}")
            return []
    
    def format_context(self, retrieved_docs: List[Dict[str, Any]]) -> str:
        """Format retrieved documents as context for the LLM.
        
        Args:
            retrieved_docs: List of retrieved documents.
            
        Returns:
            Formatted context string.
        """
        if not retrieved_docs:
            return "No relevant knowledge found."
        
        context = "Retrieved Knowledge Chunks:\n\n"
        for i, doc in enumerate(retrieved_docs, 1):
            text = doc.get('text') or doc.get('payload', {}).get('text', '')
            source = doc.get('source') or doc.get('payload', {}).get('source', 'Unknown')
            score = doc.get('score', 0)
            
            context += f"[{i}] (Score: {score:.2f}) Source: {source}\n"
            context += f"{text}\n\n"
        
        return context
