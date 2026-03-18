"""
FastAPI Backend for Endee AI Knowledge Assistant
REST API for RAG pipeline and document management.
"""

import logging
import os
from typing import Optional, List
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
import uvicorn

from endee_integration import EndeeVectorDB, get_endee_client, VectorMetadata
from openai_embeddings import OpenAIEmbeddingService, get_embedding_service
from rag_pipeline import RAGPipeline, get_rag_pipeline
from document_processor import DocumentProcessor

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# Request/Response Models
# ============================================================================

class QueryRequest(BaseModel):
    """Query request model."""
    query: str
    top_k: int = 5
    retrieve_only: bool = False
    temperature: float = 0.7
    max_tokens: int = 1000


class QueryResponse(BaseModel):
    """Query response model."""
    query: str
    answer: str
    context_chunks: List[dict]
    sources: List[str]
    retrieval_time: float
    generation_time: float
    success: bool


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    endee_connected: bool
    timestamp: str


class DocumentUploadResponse(BaseModel):
    """Document upload response."""
    filename: str
    status: str
    message: str
    chunks_created: int


# ============================================================================
# FastAPI Application Setup
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting Endee AI Knowledge Assistant")
    
    try:
        # Initialize Endee
        endee_db = await get_endee_client()
        is_healthy = await endee_db.health_check()
        
        if not is_healthy:
            logger.warning("⚠ Endee server not responding - some features may be limited")
        else:
            await endee_db.create_collection()
            logger.info("✓ Endee connection established")
        
        # Initialize embeddings
        embedding_service = get_embedding_service()
        logger.info("✓ OpenAI embeddings service ready")
        
        # Initialize RAG pipeline
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if openai_api_key:
            rag_pipeline = await get_rag_pipeline(
                endee_db=endee_db,
                embedding_service=embedding_service,
                openai_api_key=openai_api_key
            )
            logger.info("✓ RAG pipeline initialized")
        
    except Exception as e:
        logger.error(f"Startup error: {str(e)}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application")
    try:
        endee_db = await get_endee_client()
        await endee_db.close()
    except:
        pass


app = FastAPI(
    title="Endee AI Knowledge Assistant",
    description="RAG-powered knowledge assistant using Endee vector database and OpenAI",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# Health & Status Endpoints
# ============================================================================

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Check system health.
    
    Returns:
        Health status and component status.
    """
    try:
        endee_db = await get_endee_client()
        is_healthy = await endee_db.health_check()
        
        return {
            "status": "healthy" if is_healthy else "degraded",
            "endee_connected": is_healthy,
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Health check error: {str(e)}")
        return {
            "status": "unhealthy",
            "endee_connected": False,
            "timestamp": datetime.now().isoformat()
        }


@app.get("/stats")
async def get_stats():
    """Get system statistics.
    
    Returns:
        Collection statistics and system info.
    """
    try:
        endee_db = await get_endee_client()
        stats = await endee_db.get_collection_stats()
        
        return {
            "status": "success",
            "collection_stats": stats,
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# Core Query Endpoints
# ============================================================================

@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    """Process a user query with full RAG pipeline.
    
    Args:
        request: Query request with question and parameters
        
    Returns:
        Answer with context chunks and metadata.
    """
    try:
        if not request.query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        # Get RAG pipeline
        endee_db = await get_endee_client()
        embedding_service = get_embedding_service()
        openai_api_key = os.getenv("OPENAI_API_KEY")
        
        if not openai_api_key:
            raise HTTPException(status_code=500, detail="OPENAI_API_KEY not configured")
        
        rag_pipeline = RAGPipeline(
            endee_db=endee_db,
            embedding_service=embedding_service,
            openai_api_key=openai_api_key,
            top_k=request.top_k
        )
        
        # Process query
        result = await rag_pipeline.process_query(
            query=request.query,
            retrieve_only=request.retrieve_only,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Query processing error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/query/retrieve")
async def retrieve_context(query: str, top_k: int = 5):
    """Retrieve relevant context without generating an answer.
    
    Args:
        query: User query
        top_k: Number of results to retrieve
        
    Returns:
        List of relevant document chunks.
    """
    try:
        if not query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        endee_db = await get_endee_client()
        embedding_service = get_embedding_service()
        openai_api_key = os.getenv("OPENAI_API_KEY")
        
        rag_pipeline = RAGPipeline(
            endee_db=endee_db,
            embedding_service=embedding_service,
            openai_api_key=openai_api_key,
            top_k=top_k
        )
        
        context_chunks = await rag_pipeline.retrieve_context(query)
        
        return {
            "query": query,
            "results": [
                {
                    "id": chunk.id,
                    "score": chunk.score,
                    "text": chunk.text,
                    "source": chunk.metadata.source
                }
                for chunk in context_chunks
            ],
            "count": len(context_chunks)
        }
    
    except Exception as e:
        logger.error(f"Retrieval error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/query/stream")
async def stream_query(query: str):
    """Stream query results (for real-time UI updates).
    
    Args:
        query: User query
        
    Returns:
        Streaming response with text chunks.
    """
    try:
        if not query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        endee_db = await get_endee_client()
        embedding_service = get_embedding_service()
        openai_api_key = os.getenv("OPENAI_API_KEY")
        
        rag_pipeline = RAGPipeline(
            endee_db=endee_db,
            embedding_service=embedding_service,
            openai_api_key=openai_api_key
        )
        
        async def generate():
            async for chunk in rag_pipeline.process_query_streaming(query):
                yield chunk
        
        return StreamingResponse(generate(), media_type="text/event-stream")
    
    except Exception as e:
        logger.error(f"Stream error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# Document Management Endpoints
# ============================================================================

@app.post("/documents/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None
):
    """Upload and process a document.
    
    Args:
        file: Document file (txt, pdf, md)
        background_tasks: FastAPI background tasks
        
    Returns:
        Upload status and processing info.
    """
    try:
        # Validate file type
        allowed_types = {'.txt', '.pdf', '.md'}
        file_ext = Path(file.filename).suffix.lower()
        
        if file_ext not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type. Allowed: {allowed_types}"
            )
        
        # Save uploaded file
        upload_dir = "./uploads"
        os.makedirs(upload_dir, exist_ok=True)
        file_path = f"{upload_dir}/{file.filename}"
        
        with open(file_path, 'wb') as f:
            content = await file.read()
            f.write(content)
        
        # Process document in background
        if background_tasks:
            background_tasks.add_task(
                process_uploaded_document,
                file_path
            )
        
        # Quick processing
        processor = DocumentProcessor(chunk_size=512)
        document = processor.load_document(file_path)
        chunks = processor.chunk_document(document)
        
        return {
            "filename": file.filename,
            "status": "processing",
            "message": "Document uploaded and queued for processing",
            "chunks_created": len(chunks)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


async def process_uploaded_document(file_path: str):
    """Process uploaded document in background.
    
    Args:
        file_path: Path to the document file
    """
    try:
        logger.info(f"Processing uploaded document: {file_path}")
        
        # Load and chunk
        processor = DocumentProcessor(chunk_size=512)
        document = processor.load_document(file_path)
        chunks = processor.chunk_document(document)
        
        # Generate embeddings
        embedding_service = get_embedding_service()
        chunk_texts = [chunk.text for chunk in chunks]
        embeddings = await embedding_service.embed_texts_async(chunk_texts)
        
        # Store in Endee
        endee_db = await get_endee_client()
        
        vectors = []
        for chunk, embedding in zip(chunks, embeddings):
            metadata = VectorMetadata(
                document_id=document.id,
                chunk_id=chunk.id,
                text=chunk.text,
                source=document.source,
                chunk_index=chunk.chunk_index,
                total_chunks=len(chunks),
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat(),
                metadata={}
            )
            vectors.append((chunk.id, embedding, metadata))
        
        success = await endee_db.store_vectors(vectors)
        
        if success:
            logger.info(f"✓ Successfully processed and stored: {document.name}")
        else:
            logger.error(f"✗ Failed to store vectors for: {file_path}")
    
    except Exception as e:
        logger.error(f"Error processing document: {str(e)}")


@app.delete("/collections/{collection_name}")
async def delete_collection(collection_name: str):
    """Delete a collection.
    
    Args:
        collection_name: Name of collection to delete
        
    Returns:
        Deletion status.
    """
    try:
        endee_db = await get_endee_client()
        
        # Safety check - prevent deletion of main collection
        if collection_name == "knowledge_base":
            raise HTTPException(
                status_code=403,
                detail="Cannot delete the main knowledge base collection"
            )
        
        success = await endee_db.delete_collection()
        
        return {
            "status": "success" if success else "failed",
            "collection": collection_name,
            "deleted": success
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Deletion error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    logger.info(f"Starting FastAPI server on {host}:{port}")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=os.getenv("ENV") == "development"
    )
