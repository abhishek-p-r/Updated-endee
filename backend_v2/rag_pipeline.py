"""
RAG (Retrieval Augmented Generation) Pipeline
Combines Endee vector search with OpenAI LLM for intelligent Q&A.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import asyncio

from openai import AsyncOpenAI, OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

from backend_v2.endee_integration import EndeeVectorDB, SearchResult, VectorMetadata
from backend_v2.openai_embeddings import OpenAIEmbeddingService
from backend_v2.document_processor import DocumentChunk

logger = logging.getLogger(__name__)


class RAGPipeline:
    """
    Retrieval Augmented Generation Pipeline.
    
    Workflow:
    1. User asks a question
    2. Embed the question using OpenAI
    3. Search for relevant documents in Endee vector DB
    4. Retrieve the top K relevant chunks
    5. Create a prompt with retrieved context
    6. Generate answer using OpenAI GPT
    """
    
    def __init__(
        self,
        endee_db: EndeeVectorDB,
        embedding_service: OpenAIEmbeddingService,
        openai_api_key: str,
        top_k: int = 5,
        score_threshold: float = 0.5,
        model: str = "gpt-3.5-turbo"
    ):
        """Initialize RAG pipeline.
        
        Args:
            endee_db: Endee vector database instance
            embedding_service: OpenAI embedding service
            openai_api_key: OpenAI API key
            top_k: Number of documents to retrieve
            score_threshold: Minimum similarity score
            model: GPT model to use
        """
        self.endee_db = endee_db
        self.embedding_service = embedding_service
        self.openai_api_key = openai_api_key
        self.top_k = top_k
        self.score_threshold = score_threshold
        self.model = model
        
        self.client = OpenAI(api_key=openai_api_key)
        self.async_client = AsyncOpenAI(api_key=openai_api_key)
        
        logger.info(f"RAG Pipeline initialized with model: {model}")
    
    async def retrieve_context(self, query: str) -> List[SearchResult]:
        """Retrieve relevant documents for a query.
        
        Args:
            query: User query
            
        Returns:
            List of relevant document chunks
        """
        try:
            # Step 1: Embed the query
            logger.info(f"Embedding query: {query}")
            query_embedding = await self.embedding_service.embed_text_async(query)
            
            # Step 2: Search in Endee
            logger.info(f"Searching Endee for top {self.top_k} results")
            results = await self.endee_db.semantic_search(
                query_embedding=query_embedding,
                top_k=self.top_k,
                score_threshold=self.score_threshold
            )
            
            logger.info(f"Retrieved {len(results)} relevant chunks")
            return results
        
        except Exception as e:
            logger.error(f"Error retrieving context: {str(e)}")
            return []
    
    def _create_rag_prompt(
        self,
        query: str,
        context_chunks: List[SearchResult]
    ) -> str:
        """Create a prompt with retrieved context.
        
        Args:
            query: Original user query
            context_chunks: Retrieved document chunks
            
        Returns:
            Formatted prompt for LLM
        """
        context_text = "\n\n".join([
            f"[Source: {chunk.metadata.source} (Chunk {chunk.metadata.chunk_index})]\\n{chunk.text}"
            for chunk in context_chunks
        ])
        
        prompt = f"""You are a helpful knowledge assistant. Answer the user's question based on the provided context.

If the context doesn't contain relevant information, say so honestly.

Context:
{context_text}

Question: {query}

Answer:"""
        
        return prompt
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def generate_answer(
        self,
        query: str,
        context_chunks: List[SearchResult],
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> str:
        """Generate an answer using retrieved context and GPT.
        
        Args:
            query: User query
            context_chunks: Retrieved document chunks
            temperature: Model temperature (0-1)
            max_tokens: Maximum tokens in response
            
        Returns:
            Generated answer
        """
        try:
            prompt = self._create_rag_prompt(query, context_chunks)
            
            logger.info(f"Generating answer using {self.model}")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful knowledge assistant that answers questions based on provided documents."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            answer = response.choices[0].message.content
            logger.info("Answer generated successfully")
            
            return answer
        
        except Exception as e:
            logger.error(f"Error generating answer: {str(e)}")
            raise
    
    async def generate_answer_async(
        self,
        query: str,
        context_chunks: List[SearchResult],
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> str:
        """Generate an answer asynchronously.
        
        Args:
            query: User query
            context_chunks: Retrieved document chunks
            temperature: Model temperature
            max_tokens: Maximum tokens
            
        Returns:
            Generated answer
        """
        try:
            prompt = self._create_rag_prompt(query, context_chunks)
            
            response = await self.async_client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful knowledge assistant that answers questions based on provided documents."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            logger.error(f"Error in async answer generation: {str(e)}")
            raise
    
    async def process_query(
        self,
        query: str,
        retrieve_only: bool = False,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> Dict[str, Any]:
        """Complete RAG pipeline: retrieve and generate.
        
        Args:
            query: User query
            retrieve_only: If True, only retrieve context (don't generate answer)
            temperature: Model temperature
            max_tokens: Maximum tokens in response
            
        Returns:
            Dictionary with answer and metadata
        """
        try:
            # Step 1: Retrieve context
            start_time = datetime.now()
            context_chunks = await self.retrieve_context(query)
            retrieval_time = (datetime.now() - start_time).total_seconds()
            
            if not context_chunks:
                return {
                    "query": query,
                    "answer": "I couldn't find relevant information in the knowledge base to answer your question.",
                    "context_chunks": [],
                    "sources": [],
                    "retrieval_time": retrieval_time,
                    "generation_time": 0,
                    "success": False
                }
            
            result = {
                "query": query,
                "context_chunks": [
                    {
                        "id": chunk.id,
                        "score": chunk.score,
                        "text": chunk.text,
                        "source": chunk.metadata.source,
                        "chunk_index": chunk.metadata.chunk_index
                    }
                    for chunk in context_chunks
                ],
                "sources": list(set(chunk.metadata.source for chunk in context_chunks)),
                "retrieval_time": retrieval_time,
                "success": True
            }
            
            # If retrieve_only, return here
            if retrieve_only:
                result["answer"] = None
                result["generation_time"] = 0
                return result
            
            # Step 2: Generate answer
            start_time = datetime.now()
            answer = await self.generate_answer_async(
                query=query,
                context_chunks=context_chunks,
                temperature=temperature,
                max_tokens=max_tokens
            )
            generation_time = (datetime.now() - start_time).total_seconds()
            
            result["answer"] = answer
            result["generation_time"] = generation_time
            
            return result
        
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            return {
                "query": query,
                "answer": f"Error: {str(e)}",
                "context_chunks": [],
                "sources": [],
                "retrieval_time": 0,
                "generation_time": 0,
                "success": False
            }
    
    async def process_query_streaming(
        self,
        query: str,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ):
        """Process query with streaming response (for web interfaces).
        
        Args:
            query: User query
            temperature: Model temperature
            max_tokens: Maximum tokens
            
        Yields:
            Streamed text chunks
        """
        try:
            context_chunks = await self.retrieve_context(query)
            
            if not context_chunks:
                yield "I couldn't find relevant information in the knowledge base."
                return
            
            prompt = self._create_rag_prompt(query, context_chunks)
            
            with self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful knowledge assistant."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True
            ) as stream:
                for text in stream.text_stream:
                    yield text
        
        except Exception as e:
            logger.error(f"Error in streaming: {str(e)}")
            yield f"Error: {str(e)}"


# Global instance
_rag_pipeline: Optional[RAGPipeline] = None


async def get_rag_pipeline(
    endee_db: EndeeVectorDB,
    embedding_service: OpenAIEmbeddingService,
    openai_api_key: str,
    top_k: int = 5,
    model: str = "gpt-3.5-turbo"
) -> RAGPipeline:
    """Get or create RAG pipeline instance.
    
    Args:
        endee_db: Endee vector database
        embedding_service: OpenAI embedding service
        openai_api_key: OpenAI API key
        top_k: Number of documents to retrieve
        model: GPT model
        
    Returns:
        RAGPipeline instance
    """
    global _rag_pipeline
    
    if _rag_pipeline is None:
        _rag_pipeline = RAGPipeline(
            endee_db=endee_db,
            embedding_service=embedding_service,
            openai_api_key=openai_api_key,
            top_k=top_k,
            model=model
        )
    
    return _rag_pipeline
