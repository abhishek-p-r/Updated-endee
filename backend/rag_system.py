"""
Complete RAG (Retrieval-Augmented Generation) System

Integrates document processing, vector storage, semantic search,
and LLM response generation into a unified pipeline.
"""

import logging
import time
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
import asyncio

from .endee_vector_db import EndeeVectorDB, SearchResult
from .openai_client import OpenAIClient, CompletionResult
from .gemini_client import get_gemini_client
from .document_processor import DocumentProcessor, TextChunk

logger = logging.getLogger(__name__)


@dataclass
class RAGResponse:
    """Complete RAG response with answer and sources."""
    query: str
    answer: str
    retrieved_documents: List[Dict[str, Any]]
    retrieval_score: float
    response_time_ms: float
    tokens_used: int
    model: str = "gpt-4o-mini"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class RAGSystem:
    """
    Complete RAG system combining vector search with LLM generation.
    
    Workflow:
    1. User submits a query
    2. Query is converted to embedding
    3. Semantic search retrieves relevant documents from Endee
    4. Retrieved context is passed to OpenAI
    5. LLM generates context-aware response
    """
    
    def __init__(
        self,
        endee_db: EndeeVectorDB,
        openai_client: OpenAIClient,
        top_k: int = 5,
        min_score: float = 0.3
    ):
        """
        Initialize RAG system.
        
        Args:
            endee_db: Endee vector database client
            openai_client: OpenAI client
            top_k: Number of results to retrieve
            min_score: Minimum similarity score
        """
        self.endee_db = endee_db
        self.openai_client = openai_client
        self.top_k = top_k
        self.min_score = min_score
        
        logger.info(
            f"RAG System initialized "
            f"(top_k={top_k}, min_score={min_score})"
        )
    
    async def ingest_documents(self, file_paths: List[str]) -> Dict[str, Any]:
        """
        Ingest and process documents into vector database.
        
        Args:
            file_paths: List of document paths
            
        Returns:
            Ingestion statistics
        """
        start_time = time.time()
        
        try:
            logger.info(f"Starting document ingestion for {len(file_paths)} files")
            
            # Process documents
            processor = DocumentProcessor()
            text_chunks = []
            
            for file_path in file_paths:
                try:
                    doc = processor.process_document(file_path)
                    chunks = processor.get_text_chunks(doc)
                    text_chunks.extend(chunks)
                except Exception as e:
                    logger.warning(f"Skipped {file_path}: {str(e)}")
                    continue
            
            if not text_chunks:
                logger.warning("No text chunks to ingest")
                return {"success": False, "message": "No chunks created"}
            
            logger.info(f"Generated {len(text_chunks)} text chunks for embedding")
            
            # Generate embeddings
            texts = [chunk.text for chunk in text_chunks]
            embedding_results = self.openai_client.generate_embeddings_batch(texts)
            
            logger.info(f"Generated embeddings for {len(embedding_results)} chunks")
            
            # Store in Endee vector database
            vectors_to_store = [
                (
                    chunk.id,
                    emb.embedding,
                    chunk.metadata,
                    chunk.text
                )
                for chunk, emb in zip(text_chunks, embedding_results)
            ]
            
            upserted_count = await self.endee_db.upsert_batch(vectors_to_store)
            
            elapsed_time = time.time() - start_time
            
            result = {
                "success": True,
                "documents_processed": len(file_paths),
                "chunks_created": len(text_chunks),
                "vectors_stored": upserted_count,
                "time_seconds": elapsed_time,
                "embedding_model": self.openai_client.embedding_model
            }
            
            logger.info(f"Document ingestion complete: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error in document ingestion: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def retrieve(
        self,
        query: str,
        top_k: Optional[int] = None,
        min_score: Optional[float] = None
    ) -> List[SearchResult]:
        """
        Retrieve relevant documents for a query.
        
        Args:
            query: User query
            top_k: Override default top_k
            min_score: Override default min_score
            
        Returns:
            List of SearchResult objects
        """
        start_time = time.time()
        
        try:
            # Use provided values or defaults
            top_k = top_k or self.top_k
            min_score = min_score or self.min_score
            
            # Generate query embedding
            logger.debug(f"Generating embedding for query: {query[:100]}...")
            query_embedding_result = await self.openai_client.generate_embedding_async(query)
            query_embedding = query_embedding_result.embedding
            
            # Search in vector database
            logger.debug(f"Searching Endee with top_k={top_k}")
            results = await self.endee_db.search(
                query_embedding=query_embedding,
                top_k=top_k,
                min_score=min_score
            )
            
            elapsed = time.time() - start_time
            logger.info(f"Retrieved {len(results)} documents in {elapsed:.2f}s")
            
            return results
            
        except Exception as e:
            logger.error(f"Error in retrieval: {str(e)}")
            return []
    
    async def generate_response(
        self,
        query: str,
        context: List[str],
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> CompletionResult:
        """
        Generate response using retrieved context.
        
        Args:
            query: User query
            context: Retrieved context chunks
            system_prompt: System prompt override
            temperature: Response temperature
            max_tokens: Maximum tokens
            
        Returns:
            CompletionResult with answer
        """
        try:
            logger.debug(f"Generating response with {len(context)} context chunks")
            
            result = await self.openai_client.generate_response_async(
                query=query,
                context=context,
                system_prompt=system_prompt,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            logger.info(f"Generated response ({result.tokens_used} tokens)")
            return result
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            raise
    
    async def answer_question(
        self,
        query: str,
        top_k: Optional[int] = None,
        system_prompt: Optional[str] = None
    ) -> RAGResponse:
        """
        Complete RAG pipeline: retrieve and generate answer.
        
        Args:
            query: User question
            top_k: Number of results to retrieve
            system_prompt: System prompt override
            
        Returns:
            RAGResponse with answer and sources
        """
        start_time = time.time()
        
        try:
            logger.info(f"Answering question: {query}")
            
            # Retrieve relevant documents
            retrieved = await self.retrieve(query, top_k=top_k)
            
            if not retrieved:
                logger.warning("No documents retrieved")
                return RAGResponse(
                    query=query,
                    answer="No relevant information found in the knowledge base.",
                    retrieved_documents=[],
                    retrieval_score=0.0,
                    response_time_ms=0.0,
                    tokens_used=0
                )
            
            # Prepare context
            context = [result.text for result in retrieved]
            
            # Generate response
            try:
                completion = await self.generate_response(
                    query=query,
                    context=context,
                    system_prompt=system_prompt
                )
                answer = completion.answer
                tokens_used = completion.tokens_used
                model_used = completion.model
            except Exception as e:
                logger.warning(f"Primary model generation failed: {str(e)}. Falling back to Gemini.")
                gemini = get_gemini_client()
                answer = await gemini.generate_response_async(query, "\n\n".join(context)) or "I apologize, but both primary and backup AI systems are currently unavailable."
                tokens_used = 0
                model_used = "gemini-1.5-flash"
            
            # Prepare source documents
            sources = [
                {
                    "id": result.id,
                    "score": result.score,
                    "text": result.text[:200] + "...",
                    "metadata": result.metadata
                }
                for result in retrieved
            ]
            
            # Calculate average retrieval score
            avg_score = sum(r.score for r in retrieved) / len(retrieved)
            
            elapsed_ms = (time.time() - start_time) * 1000
            
            rag_response = RAGResponse(
                query=query,
                answer=answer,
                retrieved_documents=sources,
                retrieval_score=avg_score,
                response_time_ms=elapsed_ms,
                tokens_used=tokens_used,
                model=model_used
            )
            
            logger.info(
                f"Complete RAG answer generated "
                f"({len(sources)} sources, {elapsed_ms:.0f}ms)"
            )
            
            return rag_response
            
        except Exception as e:
            logger.error(f"Error in answer generation: {str(e)}")
            raise
    
    async def stream_answer(
        self,
        query: str,
        top_k: Optional[int] = None,
        system_prompt: Optional[str] = None
    ):
        """
        Stream RAG response for real-time UI updates.
        
        Args:
            query: User question
            top_k: Number of results to retrieve
            system_prompt: System prompt override
            
        Yields:
            Response chunks as generated
        """
        try:
            # Retrieve documents
            retrieved = await self.retrieve(query, top_k=top_k)
            
            if not retrieved:
                yield "No relevant information found in the knowledge base."
                return
            
            # Prepare context
            context = [result.text for result in retrieved]
            
            # Stream response
            async for chunk in self.openai_client.generate_response_stream_async(
                query=query,
                context=context,
                system_prompt=system_prompt
            ):
                yield chunk
            
        except Exception as e:
            logger.error(f"Error in stream answer: {str(e)}")
            yield f"Error: {str(e)}"
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get RAG system statistics."""
        try:
            db_stats = await self.endee_db.get_collection_stats()
            
            return {
                "vector_database": db_stats,
                "embedding_model": self.openai_client.embedding_model,
                "completion_model": self.openai_client.completion_model,
                "embedding_dimension": self.openai_client.embedding_dimension,
                "retrieval_config": {
                    "top_k": self.top_k,
                    "min_score": self.min_score
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting stats: {str(e)}")
            return {}


# Singleton instance
_rag_system: Optional[RAGSystem] = None


async def get_rag_system(
    endee_db: EndeeVectorDB,
    openai_client: OpenAIClient
) -> RAGSystem:
    """
    Get or create RAG system singleton.
    
    Args:
        endee_db: Endee vector database
        openai_client: OpenAI client
        
    Returns:
        RAGSystem instance
    """
    global _rag_system
    
    if _rag_system is None:
        _rag_system = RAGSystem(
            endee_db=endee_db,
            openai_client=openai_client
        )
    
    return _rag_system
