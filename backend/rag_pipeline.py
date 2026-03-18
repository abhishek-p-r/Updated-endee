"""RAG (Retrieval Augmented Generation) Pipeline orchestration."""
import asyncio
from typing import Dict, Any, Optional, List
from backend.bots.query_bot import QueryUnderstandingBot
from backend.bots.retrieval_bot import KnowledgeRetrievalBot
from backend.bots.reasoning_bot import ReasoningAndAnswerBot
from backend.bots.formatter_bot import ResponseFormattingBot
from backend.memory_manager import get_session_manager
from backend.embeddings import get_embedding_service
from backend.endee_client import get_endee_client
from backend.config import settings
from backend.logging_config import get_logger

logger = get_logger("rag_pipeline")


class RAGPipeline:
    """Complete RAG pipeline with multi-agent orchestration."""
    
    def __init__(self):
        """Initialize the RAG pipeline with all bots."""
        self.query_bot = QueryUnderstandingBot()
        self.retrieval_bot = KnowledgeRetrievalBot()
        self.reasoning_bot = ReasoningAndAnswerBot()
        self.formatter_bot = ResponseFormattingBot()
        self.embedding_service = get_embedding_service()
        self.session_manager = get_session_manager()
        logger.info("Initialized RAG Pipeline")
    
    async def process_query(
        self,
        question: str,
        session_id: str = "default",
        use_conversation_history: bool = True
    ) -> Dict[str, Any]:
        """Process a user query through the complete RAG pipeline.
        
        Args:
            question: The user's question.
            session_id: Session identifier for conversation history.
            use_conversation_history: Whether to use previous conversation context.
            
        Returns:
            Complete response with answer, sources, and metadata.
        """
        try:
            logger.info(f"Processing query: {question}")
            
            # Step 1: Query Understanding
            query_analysis = self.query_bot.analyze_query(question)
            optimized_query = query_analysis.get('optimized', question)
            logger.info(f"Query optimized to: {optimized_query}")
            
            # Step 2: Knowledge Retrieval
            retrieved_docs = await self.retrieval_bot.retrieve_knowledge(optimized_query)
            context = self.retrieval_bot.format_context(retrieved_docs)
            logger.info(f"Retrieved {len(retrieved_docs)} documents")
            
            # Step 3: Get conversation history if enabled
            conversation_history = None
            if use_conversation_history:
                session = self.session_manager.get_or_create_session(session_id)
                conversation_history = session.get_conversation_context()
            
            # Step 4: Reasoning and Answer Generation
            answer = self.reasoning_bot.generate_answer(
                question=question,
                context=context,
                conversation_history=conversation_history
            )
            
            if not answer:
                answer = "I couldn't generate an answer at this time. Please try again."
                logger.warning("Failed to generate answer")
            
            # Step 5: Response Formatting
            sources = [
                {
                    "text": doc.get('text') or doc.get('payload', {}).get('text', ''),
                    "source": doc.get('source') or doc.get('payload', {}).get('source', 'Unknown'),
                    "score": doc.get('score', 0)
                }
                for doc in retrieved_docs
            ]
            
            formatted_response = self.formatter_bot.format_response(answer, sources)
            
            # Store in conversation memory
            session = self.session_manager.get_or_create_session(session_id)
            session.add_message("user", question)
            session.add_message("assistant", answer)
            
            result = {
                "success": True,
                "question": question,
                "query_analysis": query_analysis,
                "answer": answer,
                "formatted": formatted_response,
                "retrieved_documents_count": len(retrieved_docs),
                "sources": sources,
                "conversation_history_used": use_conversation_history
            }
            
            logger.info("Query processed successfully")
            return result
        
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "question": question
            }
    
    async def ingest_documents(
        self,
        documents: List[Dict[str, str]],
        chunk_size: int = None,
        chunk_overlap: int = None
    ) -> Dict[str, Any]:
        """Ingest documents into the vector database.
        
        Args:
            documents: List of documents with 'text' and optional 'source' fields.
            chunk_size: Size of text chunks.
            chunk_overlap: Overlap between chunks.
            
        Returns:
            Ingestion result with statistics.
        """
        try:
            chunk_size = chunk_size or settings.chunk_size
            chunk_overlap = chunk_overlap or settings.chunk_overlap
            
            logger.info(f"Starting document ingestion: {len(documents)} documents")
            
            # Chunk documents
            chunks = []
            chunk_id = 0
            
            for doc_idx, doc in enumerate(documents):
                text = doc.get('text', '')
                source = doc.get('source', f'document_{doc_idx}')
                
                # Simple chunking
                for i in range(0, len(text), chunk_size - chunk_overlap):
                    chunk_text = text[i:i + chunk_size]
                    if chunk_text.strip():
                        chunks.append({
                            "chunk_id": chunk_id,
                            "document_id": doc_idx,
                            "text": chunk_text,
                            "source": source
                        })
                        chunk_id += 1
            
            logger.info(f"Created {len(chunks)} chunks from {len(documents)} documents")
            
            # Generate embeddings
            texts = [chunk['text'] for chunk in chunks]
            embeddings = self.embedding_service.generate_embeddings_batch(texts)
            
            # Prepare vectors for Endee
            vectors = []
            for chunk, embedding in zip(chunks, embeddings):
                vectors.append({
                    "id": str(chunk['chunk_id']),
                    "vector": embedding,
                    "payload": {
                        "document_id": chunk['document_id'],
                        "text": chunk['text'],
                        "source": chunk['source'],
                        "chunk_id": chunk['chunk_id']
                    }
                })
            
            # Upsert to Endee
            endee_client = await get_endee_client()
            success = await endee_client.upsert_vectors(vectors)
            
            if success:
                logger.info(f"Successfully ingested {len(vectors)} vectors")
                return {
                    "success": True,
                    "documents_ingested": len(documents),
                    "chunks_created": len(chunks),
                    "vectors_stored": len(vectors)
                }
            else:
                logger.error("Failed to upsert vectors to Endee")
                return {
                    "success": False,
                    "error": "Failed to store vectors in Endee"
                }
        
        except Exception as e:
            logger.error(f"Error ingesting documents: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }


# Global pipeline instance
_rag_pipeline = None


def get_rag_pipeline() -> RAGPipeline:
    """Get or create the RAG pipeline singleton."""
    global _rag_pipeline
    if _rag_pipeline is None:
        _rag_pipeline = RAGPipeline()
    return _rag_pipeline
