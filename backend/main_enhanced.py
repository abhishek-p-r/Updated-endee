"""
Enhanced FastAPI Backend for AI Chatbot Pro v3
Features:
- Dual AI (OpenAI + Gemini)
- Web Search Integration
- AI Insights Engine
- Document Q&A
- Real-time Streaming
"""

from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import json
import os
from datetime import datetime
import asyncio
import base64
from io import BytesIO

# AI Libraries
import openai
from google import genai
import requests
from bs4 import BeautifulSoup

# Document processing
try:
    import PyPDF2
except:
    pass

# ============================================================================
# Configuration & Models
# ============================================================================

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyD0xYhPfQAoolmYQ6S6zTHgUOsoTa6acIs")

app = FastAPI(
    title="AI Chatbot Pro v3",
    description="Advanced AI with Web Search, Insights & Document Q&A",
    version="3.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response Models
class ChatRequest(BaseModel):
    question: str
    use_web_search: bool = True
    use_insights: bool = True
    documents: Optional[List[Dict]] = None


class InsightRequest(BaseModel):
    topic: str
    depth: str = "medium"  # light, medium, deep


class DocumentQARequest(BaseModel):
    question: str
    document_content: str
    document_name: str = "document.txt"


class SearchRequest(BaseModel):
    query: str
    num_results: int = 5


# ============================================================================
# AI Clients
# ============================================================================

class AIClient:
    """Unified AI client for OpenAI and Gemini"""
    
    def __init__(self):
        self.openai_key = OPENAI_API_KEY
        self.gemini_key = GEMINI_API_KEY
        self.setup_gemini()
    
    def setup_gemini(self):
        """Initialize Gemini client"""
        try:
            if self.gemini_key:
                genai.configure(api_key=self.gemini_key)
                self.gemini_model = genai.GenerativeModel("gemini-2.0-flash")
        except Exception as e:
            print(f"Gemini setup error: {e}")
            self.gemini_model = None
    
    async def generate(self, prompt: str, model: str = "auto") -> dict:
        """Generate response using AI"""
        try:
            # Try OpenAI first
            if self.openai_key and model in ["auto", "openai"]:
                try:
                    openai.api_key = self.openai_key
                    response = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role": "user", "content": prompt}],
                        max_tokens=500,
                        temperature=0.7
                    )
                    return {
                        "text": response.choices[0].message.content,
                        "model": "OpenAI GPT-3.5-turbo",
                        "source": "openai"
                    }
                except Exception as e:
                    print(f"OpenAI error: {e}")
            
            # Fallback to Gemini
            if self.gemini_model and model in ["auto", "gemini"]:
                try:
                    response = self.gemini_model.generate_content(prompt)
                    return {
                        "text": response.text,
                        "model": "Google Gemini 2.0 Flash",
                        "source": "gemini"
                    }
                except Exception as e:
                    print(f"Gemini error: {e}")
            
            # Demo response fallback
            return await self.get_demo_response(prompt)
        
        except Exception as e:
            return {
                "text": f"Error generating response: {str(e)}",
                "model": "Demo Mode",
                "source": "error"
            }
    
    async def get_demo_response(self, query: str) -> dict:
        """Generate intelligent demo response"""
        responses = {
            "hello": "Hello! 👋 I'm your advanced AI assistant. I can help with chat, web search, document analysis, and AI insights. What would you like to explore?",
            "help": "I can help with:\n• 💬 Chat - Natural conversations\n• 🔍 Web Search - Real-time information\n• 📊 AI Insights - Deep analysis\n• 📄 Document Q&A - Ask about documents\n• 🤖 Smart Features - Advanced problem solving",
            "what can you do": "I can:\n1. Answer questions with AI\n2. Search the web in real-time\n3. Generate AI insights on any topic\n4. Analyze PDF and text documents\n5. Provide smart recommendations\n6. Explain complex topics\n7. Generate creative content",
            "demo": "This is demo mode - showing system is fully functional! With real API keys, all responses are from OpenAI or Gemini."
        }
        
        query_lower = query.lower()
        for key, response in responses.items():
            if key in query_lower:
                return {
                    "text": response,
                    "model": "Demo Mode",
                    "source": "demo"
                }
        
        return {
            "text": f"Demo Response: '{query}' - System is working! With real API keys, you'll get AI-powered responses.",
            "model": "Demo Mode",
            "source": "demo"
        }


class WebSearchEngine:
    """Search the web for real-time information"""
    
    @staticmethod
    async def search(query: str, num_results: int = 5) -> List[Dict]:
        """Perform web search"""
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            url = f"https://www.bing.com/search?q={query}"
            response = requests.get(url, headers=headers, timeout=5)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, "html.parser")
                results = []
                
                for item in soup.find_all("li", class_="b_algo")[:num_results]:
                    title = item.find("h2")
                    link = item.find("a")
                    snippet = item.find("p")
                    
                    if title and link:
                        results.append({
                            "title": title.text,
                            "url": link.get("href", ""),
                            "snippet": snippet.text if snippet else ""
                        })
                
                return results if results else await WebSearchEngine.get_demo_search()
            
            return await WebSearchEngine.get_demo_search()
        
        except Exception as e:
            print(f"Web search error: {e}")
            return await WebSearchEngine.get_demo_search()
    
    @staticmethod
    async def get_demo_search() -> List[Dict]:
        """Return demo search results"""
        return [
            {
                "title": "Demo Search Result 1",
                "url": "https://example.com/result1",
                "snippet": "This is a demo search result. With web access, real results would appear here."
            },
            {
                "title": "Demo Search Result 2",
                "url": "https://example.com/result2",
                "snippet": "Demonstrating the web search capability of your AI chatbot."
            },
            {
                "title": "Demo Search Result 3",
                "url": "https://example.com/result3",
                "snippet": "Enable real web search to get actual internet results."
            }
        ]


class InsightsEngine:
    """UNIQUE FEATURE: AI-powered insights and analysis"""
    
    def __init__(self, ai_client: AIClient):
        self.ai = ai_client
    
    async def generate_insights(self, topic: str, depth: str = "medium") -> dict:
        """Generate AI insights on any topic"""
        
        prompts = {
            "light": f"Give a brief 100-word overview of: {topic}",
            "medium": f"Provide a detailed 300-word analysis of: {topic}. Include key points and implications.",
            "deep": f"Provide an in-depth 500-word analysis of: {topic}. Include history, current state, implications, and future trends."
        }
        
        prompt = prompts.get(depth, prompts["medium"])
        
        # Get AI response
        response = await self.ai.generate(prompt)
        
        return {
            "topic": topic,
            "depth": depth,
            "insight": response["text"],
            "model": response["model"],
            "generated_at": datetime.now().isoformat()
        }


class DocumentProcessor:
    """Process and analyze documents"""
    
    @staticmethod
    async def process_upload(file_content: bytes, filename: str) -> Dict:
        """Process uploaded document"""
        try:
            if filename.endswith('.pdf'):
                return await DocumentProcessor.process_pdf(file_content)
            else:
                text = file_content.decode('utf-8')
                return {
                    "content": text[:2000],  # First 2000 chars
                    "type": "text",
                    "size": len(text),
                    "preview": text[:500] + "..." if len(text) > 500 else text
                }
        except Exception as e:
            return {
                "error": str(e),
                "type": "error"
            }
    
    @staticmethod
    async def process_pdf(pdf_content: bytes) -> Dict:
        """Extract text from PDF"""
        try:
            pdf = BytesIO(pdf_content)
            reader = PyPDF2.PdfReader(pdf)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
            
            return {
                "content": text[:2000],
                "type": "pdf",
                "pages": len(reader.pages),
                "size": len(text),
                "preview": text[:500] + "..." if len(text) > 500 else text
            }
        except Exception as e:
            return {
                "error": str(e),
                "type": "error"
            }


# ============================================================================
# Initialize Services
# ============================================================================

ai_client = AIClient()
search_engine = WebSearchEngine()
insights_engine = InsightsEngine(ai_client)
doc_processor = DocumentProcessor()


# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check"""
    return {
        "status": "healthy",
        "service": "AI Chatbot Pro v3",
        "version": "3.0.0",
        "features": ["chat", "web_search", "ai_insights", "document_qa"],
        "timestamp": datetime.now().isoformat()
    }


@app.post("/chat")
async def chat(request: ChatRequest):
    """Chat with AI with optional web search and insights"""
    try:
        response_data = {
            "question": request.question,
            "timestamp": datetime.now().isoformat(),
            "features_used": []
        }
        
        # Main AI response
        chat_response = await ai_client.generate(request.question)
        response_data["answer"] = chat_response["text"]
        response_data["model"] = chat_response["model"]
        response_data["source"] = chat_response["source"]
        
        # Add web search if requested
        if request.use_web_search:
            search_results = await search_engine.search(request.question)
            response_data["web_search"] = search_results
            response_data["features_used"].append("web_search")
        
        # Add insights if requested
        if request.use_insights:
            insights = await insights_engine.generate_insights(request.question, "light")
            response_data["insights"] = insights["insight"]
            response_data["features_used"].append("ai_insights")
        
        # Add document Q&A if documents provided
        if request.documents:
            doc_qa = await process_document_qa(request.question, request.documents[0])
            response_data["document_qa"] = doc_qa
            response_data["features_used"].append("document_qa")
        
        return JSONResponse(content=response_data)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/insights")
async def get_insights(request: InsightRequest):
    """Generate AI insights on a topic"""
    try:
        insights = await insights_engine.generate_insights(request.topic, request.depth)
        return JSONResponse(content=insights)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/search")
async def web_search(request: SearchRequest):
    """Search the web"""
    try:
        results = await search_engine.search(request.query, request.num_results)
        return JSONResponse(content={
            "query": request.query,
            "results": results,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/document-qa")
async def document_qa(request: DocumentQARequest):
    """Ask questions about a document"""
    try:
        prompt = f"""Based on this document content:
        
{request.document_content}

Please answer this question: {request.question}

Provide a focused answer based on the document content."""
        
        response = await ai_client.generate(prompt)
        
        return JSONResponse(content={
            "question": request.question,
            "document": request.document_name,
            "answer": response["text"],
            "model": response["model"],
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/upload-document")
async def upload_document(file: UploadFile = File(...)):
    """Upload and process a document"""
    try:
        content = await file.read()
        result = await doc_processor.process_upload(content, file.filename)
        
        return JSONResponse(content={
            "filename": file.filename,
            "size": result.get("size", 0),
            "type": result.get("type"),
            "preview": result.get("preview"),
            "content": result.get("content"),
            "processed_at": datetime.now().isoformat()
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def process_document_qa(question: str, document: Dict) -> str:
    """Process Q&A on document"""
    try:
        content = document.get("content", "")
        prompt = f"""Document: {document.get('name', 'unknown')}
        
{content}

Question: {question}

Answer:"""
        
        response = await ai_client.generate(prompt)
        return response["text"]
    except Exception as e:
        return f"Error processing document: {str(e)}"


@app.get("/")
async def root():
    """API Info"""
    return {
        "name": "AI Chatbot Pro v3",
        "description": "Advanced AI with Web Search, Insights & Document Q&A",
        "endpoints": {
            "/health": "Health check",
            "/chat": "Chat with AI (POST)",
            "/insights": "Generate insights (POST)",
            "/search": "Web search (POST)",
            "/document-qa": "Ask about documents (POST)",
            "/upload-document": "Upload document (POST)"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
