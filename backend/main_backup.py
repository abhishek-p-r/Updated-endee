"""FastAPI backend for Endee AI Knowledge Assistant."""
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import PyPDF2
import io

from backend.config import settings
from backend.rag_pipeline import get_rag_pipeline
from backend.endee_client import get_endee_client
from backend.logging_config import get_logger
from backend.analytics import get_analytics
from backend.cache_manager import get_query_cache
from backend.query_optimizer import get_query_optimizer

logger = get_logger("main")

# Initialize FastAPI app
app = FastAPI(
    title="Endee AI Knowledge Assistant",
    description="Multi-Agent RAG System powered by Endee Vector Database",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models
class QuestionRequest(BaseModel):
    """Request model for asking questions."""
    question: str
    session_id: str = "default"
    use_conversation_history: bool = True


class DocumentRequest(BaseModel):
    """Request model for ingesting documents."""
    documents: List[dict]
    chunk_size: Optional[int] = None
    chunk_overlap: Optional[int] = None


class HealthResponse(BaseModel):
    """Health check response model."""
    status: str
    service: str
    version: str
    endee_connected: bool


# Routes
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    try:
        endee_client = await get_endee_client()
        endee_connected = await endee_client.health_check()
        
        return HealthResponse(
            status="healthy",
            service="Endee AI Knowledge Assistant",
            version="1.0.0",
            endee_connected=endee_connected
        )
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return HealthResponse(
            status="unhealthy",
            service="Endee AI Knowledge Assistant",
            version="1.0.0",
            endee_connected=False
        )


@app.post("/ask")
async def ask_question(request: QuestionRequest):
    """Process a user question through the RAG pipeline.
    
    Args:
        request: Question request with optional session ID.
        
    Returns:
        RAG pipeline response with answer and sources.
    """
    try:
        if not request.question.strip():
            raise HTTPException(status_code=400, detail="Question cannot be empty")
        
        # Check cache first
        cache = get_query_cache()
        cached_result = cache.get(request.question)
        if cached_result:
            logger.info(f"Returning cached result for: {request.question}")
            return JSONResponse(content=cached_result)
        
        # Start analytics
        analytics = get_analytics()
        start_time = analytics.record_query_start()
        
        # Optimize query
        optimizer = get_query_optimizer()
        validation = optimizer.validate_query(request.question)
        optimal_params = optimizer.get_optimal_parameters(request.question)
        
        pipeline = get_rag_pipeline()
        result = await pipeline.process_query(
            question=request.question,
            session_id=request.session_id,
            use_conversation_history=request.use_conversation_history
        )
        
        # Record analytics
        success = result.get("success", False)
        retrieved_count = result.get("retrieved_documents_count", 0)
        analytics.record_query_end(start_time, request.question, success, retrieved_count)
        
        # Cache successful results
        if success:
            cache.set(request.question, result)
        
        result["optimization"] = {
            "validation": validation,
            "optimal_parameters": optimal_params
        }
        
        return JSONResponse(content=result)
    
    except Exception as e:
        logger.error(f"Error processing question: {str(e)}")
        analytics = get_analytics()
        analytics.record_query_end(start_time, request.question, False, 0)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ingest")
async def ingest_documents(request: DocumentRequest):
    """Ingest documents into the vector database.
    
    Args:
        request: Document request with list of documents.
        
    Returns:
        Ingestion result with statistics.
    """
    try:
        if not request.documents:
            raise HTTPException(status_code=400, detail="No documents provided")
        
        pipeline = get_rag_pipeline()
        result = await pipeline.ingest_documents(
            documents=request.documents,
            chunk_size=request.chunk_size,
            chunk_overlap=request.chunk_overlap
        )
        
        return JSONResponse(content=result)
    
    except Exception as e:
        logger.error(f"Error ingesting documents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ingest/upload")
async def upload_and_ingest(
    file: UploadFile = File(...),
    source: Optional[str] = None
):
    """Upload and ingest a document file (PDF or TXT).
    
    Args:
        file: The file to upload.
        source: Optional source identifier.
        
    Returns:
        Ingestion result.
    """
    try:
        content = await file.read()
        source = source or file.filename
        
        # Handle PDF files
        if file.filename.endswith('.pdf'):
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
        
        # Handle text files
        elif file.filename.endswith(('.txt', '.md')):
            text = content.decode('utf-8')
        
        else:
            raise HTTPException(
                status_code=400,
                detail="Unsupported file type. Use PDF, TXT, or MD files."
            )
        
        pipeline = get_rag_pipeline()
        result = await pipeline.ingest_documents(
            documents=[{"text": text, "source": source}]
        )
        
        return JSONResponse(content=result)
    
    except Exception as e:
        logger.error(f"Error uploading document: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/chat/history/{session_id}")
async def get_chat_history(session_id: str):
    """Get chat history for a session.
    
    Args:
        session_id: The session identifier.
        
    Returns:
        List of messages in the session.
    """
    try:
        from backend.memory_manager import get_session_manager
        
        session_manager = get_session_manager()
        session = session_manager.get_or_create_session(session_id)
        messages = session.get_messages()
        
        return {"session_id": session_id, "messages": messages}
    
    except Exception as e:
        logger.error(f"Error getting chat history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/chat/history/{session_id}")
async def clear_chat_history(session_id: str):
    """Clear chat history for a session.
    
    Args:
        session_id: The session identifier.
        
    Returns:
        Confirmation of deletion.
    """
    try:
        from backend.memory_manager import get_session_manager
        
        session_manager = get_session_manager()
        session_manager.delete_session(session_id)
        
        return {"message": f"Chat history cleared for session {session_id}"}
    
    except Exception as e:
        logger.error(f"Error clearing chat history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/analytics/stats")
async def get_analytics_stats():
    """Get system analytics and statistics.
    
    Returns:
        Comprehensive system metrics and performance stats.
    """
    try:
        analytics = get_analytics()
        cache = get_query_cache()
        
        return {
            "system_stats": analytics.get_system_stats(),
            "cache_stats": cache.get_stats(),
            "recent_queries": analytics.get_recent_queries(5)
        }
    
    except Exception as e:
        logger.error(f"Error getting analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/analytics/report")
async def get_performance_report():
    """Get comprehensive performance report.
    
    Returns:
        Detailed performance metrics and insights.
    """
    try:
        analytics = get_analytics()
        return analytics.get_performance_report()
    
    except Exception as e:
        logger.error(f"Error generating report: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/cache/clear")
async def clear_cache():
    """Clear all query cache.
    
    Returns:
        Confirmation of cache clear.
    """
    try:
        cache = get_query_cache()
        cache.invalidate()
        return {"message": "Cache cleared successfully"}
    
    except Exception as e:
        logger.error(f"Error clearing cache: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/query/optimize")
async def optimize_query(question: str):
    """Analyze and optimize a query.
    
    Args:
        question: The query to optimize.
        
    Returns:
        Query analysis and optimization recommendations.
    """
    try:
        optimizer = get_query_optimizer()
        
        validation = optimizer.validate_query(question)
        query_type = optimizer.detect_query_type(question)
        keywords = optimizer.extract_keywords(question)
        optimal_params = optimizer.get_optimal_parameters(question)
        preprocessed = optimizer.preprocess_query(question)
        
        return {
            "original_query": question,
            "preprocessed_query": preprocessed,
            "query_type": query_type,
            "keywords": keywords,
            "validation": validation,
            "optimal_parameters": optimal_params
        }
    
    except Exception as e:
        logger.error(f"Error optimizing query: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


DEMO_RESPONSES = {
    "hello": "Hello! 👋 I'm your AI assistant powered by OpenAI and Google Gemini. I can help you with:\n• Answering questions\n• Explaining concepts\n• Problem-solving\n• Writing assistance\n• Data analysis\n\nWhat would you like help with today?",
    "how are you": "I'm functioning perfectly! 🤖 Thanks for asking. I'm ready to assist with any questions or tasks you have.",
    "what can you do": "I can help with:\n✅ Answer complex questions\n✅ Explain difficult topics\n✅ Write and edit content\n✅ Solve problems\n✅ Provide recommendations\n✅ Analyze data\n✅ Learn from uploaded documents\n\nFeel free to ask me anything!",
    "help": "I'm here to help! 💡 Here are some things you can ask me:\n\n• General questions on any topic\n• Programming and coding\n• Writing and editing\n• Math and calculations\n• History and trivia\n• Creative ideas\n• Technical explanations\n• Problem-solving assistance\n\nJust type your question and I'll do my best!",
}

def get_demo_response(question: str) -> str:
    """Get a demo response based on question keywords."""
    q_lower = question.lower().strip()
    
    for keyword, response in DEMO_RESPONSES.items():
        if keyword in q_lower:
            return response
    
    return f"""I received your question: "{question}"

**Demo Mode:** APIs are currently rate-limited, so I'm showing demo responses. 

To get full AI responses:
1. Get a paid API key from OpenAI or Google Gemini
2. Update your .env file with the new key
3. Restart the backend

In the meantime, I can help with:
• Questions that match common keywords
• General information
• Problem-solving guidance
• Navigation and feature help

Try asking about: hello, help, what can you do, how are you?"""

@app.post("/chat")
async def chat(request: QuestionRequest):
    """Chat endpoint with OpenAI (primary) → Gemini (fallback) → Demo Mode.
    
    Args:
        request: Question request.
        
    Returns:
        Chat response with answer.
    """
    try:
        query = request.question.strip()
        if not query:
            return {
                "response": "Please enter a question.",
                "source": "Error",
                "query": query,
                "error_type": "empty_query"
            }
        
        logger.info(f"Chat request: {query}")
        
        # Try OpenAI first
        try:
            logger.info("Attempting OpenAI...")
            from backend.openai_client import OpenAIClient
            
            openai_client = OpenAIClient()
            response = openai_client.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": query}],
                temperature=0.7,
                max_tokens=1000
            )
            answer = response.choices[0].message.content
            logger.info("✓ OpenAI response successful")
            
            return {
                "response": answer,
                "source": "OpenAI",
                "status": "success",
                "query": query
            }
        
        except Exception as openai_error:
            error_msg = str(openai_error).lower()
            is_quota_error = "429" in str(openai_error) or "quota" in error_msg
            
            logger.warning(f"OpenAI failed ({str(openai_error)[:50]}), trying Gemini...")
            
            # Fallback to Gemini
            try:
                logger.info("Attempting Gemini...")
                from backend.gemini_client import GeminiClient
                
                gemini_client = GeminiClient()
                gemini_response = gemini_client.generate_response(query)
                
                if gemini_response:
                    logger.info("✓ Gemini response successful")
                    return {
                        "response": gemini_response,
                        "source": "Gemini",
                        "status": "success",
                        "query": query
                    }
                else:
                    raise Exception("Gemini returned empty response")
            
            except Exception as gemini_error:
                logger.error(f"Gemini failed ({str(gemini_error)[:50]}), trying Demo Mode...")
                
                error_msg_gemini = str(gemini_error).lower()
                is_gemini_quota = "429" in str(gemini_error) or "quota" in error_msg_gemini or "resource_exhausted" in error_msg_gemini
                
                # Fallback to Demo Mode
                try:
                    demo_response = get_demo_response(query)
                    logger.info("Demo Mode response generated")
                    
                    return {
                        "response": demo_response,
                        "source": "Demo Mode",
                        "status": "demo" if (is_quota_error or is_gemini_quota) else "fallback",
                        "query": query,
                        "note": "Actual AI services are rate-limited. Showing demo response."
                    }
                except Exception as demo_error:
                    logger.error(f"Demo mode failed: {str(demo_error)}")
                    return {
                        "response": f"Unable to process request: {str(demo_error)[:100]}. Please try again later.",
                        "source": "Error",
                        "status": "error",
                        "query": query
                    }
    
    except Exception as e:
        logger.error(f"Chat endpoint error: {str(e)}")
        return {
            "response": f"Internal error: {str(e)[:80]}",
            "source": "Error",
            "status": "error",
            "query": getattr(request, 'question', 'unknown')
        }


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    logger.info("Starting up Endee AI Knowledge Assistant")
    
    try:
        endee_client = await get_endee_client()
        is_healthy = await endee_client.health_check()
        
        if is_healthy:
            logger.info("✓ Endee vector database is connected")
        else:
            logger.warning("⚠ Endee vector database is not responding")
    
    except Exception as e:
        logger.error(f"Startup error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        app,
        host=settings.server_host,
        port=settings.server_port,
        reload=settings.debug
    )
