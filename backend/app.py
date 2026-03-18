"""
FastAPI Application for Endee RAG System (Extended Version)

Features:
- Health checks, stats, vector DB management
- Document ingestion & upload
- Semantic search and QA
- Chat endpoint (supports {"query": "text"})
- Query optimization
- Streaming answers
- Dummy clients for testing without API keys
"""

import os
import logging
from typing import List, Optional, Dict, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import uvicorn
from dotenv import load_dotenv

# ---------------------------------------
# Load .env file
# ---------------------------------------
load_dotenv()  # Loads OPENAI_API_KEY, GEMINI_API_KEY, etc.

# ---------------------------------------
# Logging Configuration
# ---------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("endee_rag")

# ---------------------------------------
# Dummy / Real Client Implementations
# ---------------------------------------
class OpenAIClient:
    """Simple OpenAI client with dummy fallback."""
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            logger.warning("OPENAI_API_KEY not set, using dummy responses.")
            self.api_key = "demo-key"
            self.is_dummy = True
        else:
            self.is_dummy = False

    async def generate_answer(self, query: str, context: str = "") -> Dict[str, str]:
        if self.is_dummy:
            return {"answer": f"[DUMMY] Answer for: {query}", "context_used": context}
        # Real OpenAI API call can go here
        return {"answer": f"[REAL] Answer for: {query}", "context_used": context}


def get_openai_client() -> OpenAIClient:
    return OpenAIClient()


class EndeeVectorDB:
    """Dummy vector DB client."""
    async def health_check(self) -> bool:
        return True

    async def close(self):
        pass

    async def get_collection_stats(self) -> Dict[str, Any]:
        return {"vectors": 0}

    async def clear_collection(self) -> bool:
        return True


async def get_endee_client(host="localhost", port=8000) -> EndeeVectorDB:
    return EndeeVectorDB()


class DummyResponse:
    def __init__(self, answer="Dummy answer"):
        self.answer = answer

    def to_dict(self) -> Dict[str, str]:
        return {"answer": self.answer}


class RAGSystem:
    """Dummy RAG system."""
    async def get_stats(self) -> Dict[str, Any]:
        return {"status": "ok"}

    async def ingest_documents(self, docs: List[str]) -> Dict[str, int]:
        return {"ingested": len(docs)}

    async def answer_question(self, query: str, top_k: int = 5) -> DummyResponse:
        return DummyResponse(f"Answer for: {query}")

    async def retrieve(self, query: str, top_k: int = 5, min_score: float = 0.3) -> List[Dict[str, Any]]:
        return []

    async def stream_answer(self, query: str, top_k: int = 5):
        for i in range(3):
            yield f"Streaming chunk {i+1} for: {query}\n"

async def get_rag_system(endee_db: EndeeVectorDB, openai_client: OpenAIClient) -> RAGSystem:
    return RAGSystem()

# ---------------------------------------
# Global Instances
# ---------------------------------------
endee_db: Optional[EndeeVectorDB] = None
openai_client: Optional[OpenAIClient] = None
rag_system: Optional[RAGSystem] = None

# ---------------------------------------
# FastAPI Models
# ---------------------------------------
class QuestionRequest(BaseModel):
    question: Optional[str] = None
    query: Optional[str] = None
    top_k: Optional[int] = 5
    min_score: Optional[float] = 0.3


class IngestRequest(BaseModel):
    file_paths: Optional[List[str]] = None
    text: Optional[str] = None
    chunk_size: Optional[int] = 500
    chunk_overlap: Optional[int] = 50


class QueryOptimizeRequest(BaseModel):
    query: str

# ---------------------------------------
# App Lifecycle
# ---------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    global endee_db, openai_client, rag_system

    logger.info("Starting Endee RAG API Server...")
    try:
        endee_db = await get_endee_client()
        openai_client = get_openai_client()
        rag_system = await get_rag_system(endee_db, openai_client)
        logger.info("All services initialized successfully")
    except Exception as e:
        logger.error(f"Initialization failed: {e}")
        raise
    yield
    if endee_db:
        await endee_db.close()
    logger.info("Shutdown complete")


# ---------------------------------------
# FastAPI App
# ---------------------------------------
app = FastAPI(title="Endee RAG API", version="1.0.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True
)

# ---------------------------------------
# Health & Stats Endpoints
# ---------------------------------------
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "rag_ready": rag_system is not None,
        "openai_configured": openai_client is not None,
        "endee_connected": await endee_db.health_check() if endee_db else False
    }

@app.get("/stats")
async def system_stats():
    if not rag_system:
        raise HTTPException(status_code=503, detail="RAG system not initialized")
    return await rag_system.get_stats()

# ---------------------------------------
# Document Endpoints
# ---------------------------------------
@app.post("/ingest")
async def ingest_documents(request: IngestRequest):
    if not rag_system:
        raise HTTPException(status_code=503, detail="RAG system not initialized")
    docs = []
    if request.text:
        import tempfile
        fd, temp_path = tempfile.mkstemp(suffix=".txt")
        with os.fdopen(fd, "w") as f:
            f.write(request.text)
        docs.append(temp_path)
    if request.file_paths:
        docs.extend(request.file_paths)
    if not docs:
        raise HTTPException(status_code=400, detail="No documents provided")
    return await rag_system.ingest_documents(docs)

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    if not rag_system:
        raise HTTPException(status_code=503, detail="RAG system not initialized")
    upload_dir = "/tmp/uploads"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, file.filename)
    with open(file_path, "wb") as f:
        f.write(await file.read())
    return await rag_system.ingest_documents([file_path])

# ---------------------------------------
# Query / Chat Endpoints
# ---------------------------------------
@app.post("/ask")
async def ask_question(request: QuestionRequest):
    if not rag_system:
        raise HTTPException(status_code=503, detail="RAG system not initialized")
    query = request.question or request.query
    if not query:
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    response = await rag_system.answer_question(query=query, top_k=request.top_k)
    return response.to_dict()

@app.post("/search")
async def semantic_search(request: QuestionRequest):
    if not rag_system:
        raise HTTPException(status_code=503, detail="RAG system not initialized")
    query = request.question or request.query
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    results = await rag_system.retrieve(query=query, top_k=request.top_k, min_score=request.min_score)
    return {"query": query, "results_count": len(results), "results": results}

@app.post("/stream")
async def stream_answer(request: QuestionRequest):
    if not rag_system:
        raise HTTPException(status_code=503, detail="RAG system not initialized")
    query = request.question or request.query
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    async def generator():
        async for chunk in rag_system.stream_answer(query=query, top_k=request.top_k):
            yield chunk
    return StreamingResponse(generator(), media_type="text/event-stream")

@app.post("/chat")
async def chat(request: dict):
    # Fallback to 'question' to support standard frontend payloads
    query = request.get("query") or request.get("question")
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    if not rag_system:
        raise HTTPException(status_code=503, detail="RAG system not initialized")
    response = await rag_system.answer_question(query=query)
    return {
        "response": response.answer,
        "source": "AI Assistant",
        "status": "success",
        "query": query
    }

# ---------------------------------------
# Query Optimization
# ---------------------------------------
@app.post("/optimize-query")
async def optimize_query(request: QueryOptimizeRequest):
    original = request.query
    optimized = original.strip().lower()
    keywords = [w for w in optimized.split() if len(w) > 3]
    return {
        "original_query": original,
        "optimized_query": optimized,
        "keywords": keywords,
        "suggestions": [
            "Use specific keywords",
            "Keep query concise",
            "Remove stop words",
            "Use clear questions"
        ]
    }

# ---------------------------------------
# Vector DB Endpoints
# ---------------------------------------
@app.get("/vectors/stats")
async def vector_stats():
    if not endee_db:
        raise HTTPException(status_code=503, detail="Vector DB not initialized")
    return await endee_db.get_collection_stats()

@app.post("/vectors/clear")
async def clear_vectors():
    if not endee_db:
        raise HTTPException(status_code=503, detail="Vector DB not initialized")
    success = await endee_db.clear_collection()
    if success:
        return {"message": "Vectors cleared successfully"}
    raise HTTPException(status_code=500, detail="Failed to clear vectors")

# ---------------------------------------
# Root Endpoint
# ---------------------------------------
@app.get("/")
async def root():
    return {
        "name": "Endee RAG API",
        "version": "1.0.0",
        "endpoints": [
            "/health", "/stats", "/ingest", "/upload", "/ask",
            "/search", "/stream", "/chat"
        ]
    }

# ---------------------------------------
# Main
# ---------------------------------------
if __name__ == "__main__":
    port = int(os.getenv("API_PORT", 8000))
    host = os.getenv("API_HOST", "0.0.0.0")
    uvicorn.run("backend.app:app", host=host, port=port, reload=True)