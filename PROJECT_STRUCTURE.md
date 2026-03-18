# Project Structure & File Guide

## 📋 Overview

```
endee-ai-knowledge-assistant/
├── 📚 Documentation
│   ├── AI_KNOWLEDGE_ASSISTANT_README.md    # Main project documentation
│   ├── QUICKSTART.md                       # 5-minute setup guide
│   ├── DEVELOPMENT.md                      # Developer guide
│   └── PROJECT_STRUCTURE.md               # This file
│
├── 🔧 Backend (FastAPI + AI)
│   └── backend/
│       ├── __init__.py
│       ├── main.py                        # FastAPI app, routes, server setup
│       ├── config.py                      # Environment and settings management
│       ├── rag_pipeline.py                # RAG orchestration and workflow
│       ├── embeddings.py                  # SentenceTransformers embedding service
│       ├── endee_client.py                # Endee vector database HTTP client
│       ├── gemini_client.py               # Google Gemini AI integration
│       ├── memory_manager.py              # Conversation history and sessions
│       ├── logging_config.py              # Logging setup and configuration
│       └── bots/                          # AI Agent Bots
│           ├── __init__.py
│           ├── query_bot.py               # Query understanding & optimization
│           ├── retrieval_bot.py           # Knowledge retrieval from Endee
│           ├── reasoning_bot.py           # Answer generation with Gemini
│           └── formatter_bot.py           # Response formatting & insights
│
├── 🎨 Frontend (Streamlit UI)
│   └── frontend/
│       └── streamlit_app.py               # Web interface for chat and uploads
│
├── 🔄 Scripts & Utilities
│   └── scripts/
│       └── ingest_documents.py            # Batch document ingestion utility
│
├── 💾 Data & Logs
│   ├── data/
│   │   └── knowledge_base/               # Storage for uploaded documents
│   └── logs/                             # Application logs
│
├── 🐳 Deployment & Configuration
│   ├── Dockerfile                        # Container image definition
│   ├── docker-compose-app.yml            # Multi-service Docker setup
│   ├── start.sh                          # Convenient startup script
│   ├── requirements.txt                  # Python dependencies
│   └── .env.example                      # Environment variable template
│
└── 📖 Documentation Files
    ├── README.md                         # Original Endee repo README
    └── [Endee source code - C++ implementation]
```

## 📄 File Descriptions

### Documentation Files

| File | Purpose |
|------|---------|
| **QUICKSTART.md** | 5-minute setup guide for getting started |
| **AI_KNOWLEDGE_ASSISTANT_README.md** | Complete project documentation with all details |
| **DEVELOPMENT.md** | Developer guide for understanding and extending the system |
| **PROJECT_STRUCTURE.md** | This file - overview of all project files |

### Backend Core

| File | Purpose |
|------|---------|
| **main.py** | FastAPI application with all REST API endpoints |
| **config.py** | Settings management using Pydantic |
| **rag_pipeline.py** | Main RAG workflow orchestration |
| **embeddings.py** | SentenceTransformers embedding generation |
| **endee_client.py** | HTTP client for Endee vector database |
| **gemini_client.py** | Google Gemini API wrapper |
| **memory_manager.py** | Conversation history and session management |
| **logging_config.py** | Logging setup with file and console handlers |

### AI Bots

| File | Purpose | Responsibility |
|------|---------|-----------------|
| **query_bot.py** | Query Understanding Bot | Intent detection, query optimization, noise removal |
| **retrieval_bot.py** | Knowledge Retrieval Bot | Embedding generation, database search, context formatting |
| **reasoning_bot.py** | Reasoning & Answer Bot | Answer generation using Gemini AI |
| **formatter_bot.py** | Response Formatting Bot | Output formatting, key points, insights |

### Frontend

| File | Purpose |
|------|---------|
| **streamlit_app.py** | Complete Streamlit web UI with chat, uploads, and settings |

### Scripts & Utilities

| File | Purpose |
|------|---------|
| **ingest_documents.py** | CLI tool for batch document ingestion |

### Configuration & Deployment

| File | Purpose |
|------|---------|
| **requirements.txt** | Python package dependencies |
| **.env.example** | Environment variable template |
| **Dockerfile** | Docker image definition for containerization |
| **docker-compose-app.yml** | Docker Compose configuration for multi-service deployment |
| **start.sh** | Bash script for convenient startup |

## 🔍 Key Components Explained

### Backend Architecture

```
FastAPI Server (main.py)
├── Health Check Endpoint
├── Ask Question Endpoint
│   └── Uses RAG Pipeline
├── Document Ingest Endpoints
│   └── File upload & batch ingestion
└── Chat History Endpoints
    └── Session management
```

### RAG Pipeline Flow

```
RAGPipeline (rag_pipeline.py)
├── process_query()
│   ├── Query Understanding Bot
│   │   └── Analyzes intent
│   ├── Knowledge Retrieval Bot
│   │   ├── Generate embeddings
│   │   └── Search Endee database
│   ├── Reasoning & Answer Bot
│   │   └── Generate with Gemini
│   ├── Response Formatting Bot
│   │   └── Format output
│   └── Memory Manager
│       └── Store conversation
│
└── ingest_documents()
    ├── Chunk documents
    ├── Generate embeddings
    └── Store in Endee
```

### Service Initialization

```python
# Global instances (singletons)
get_embedding_service()      # SentenceTransformers
get_endee_client()           # Endee vector database
get_gemini_client()          # Gemini AI
get_rag_pipeline()           # Complete RAG system
get_session_manager()        # Conversation memory
```

## 🗂️ Data Flow

### Question to Answer

```
1. User asks question (Streamlit UI)
   ↓
2. POST /ask (FastAPI)
   ↓
3. RAG Pipeline processes:
   a. Query Bot: Optimize question
   b. Retrieval Bot: Search vector DB
   c. Reasoning Bot: Generate answer
   d. Formatter Bot: Structure response
   ↓
4. JSON response returned
   ↓
5. Streamlit displays answer + sources
```

### Document Upload to Storage

```
1. User uploads file (Streamlit UI)
   ↓
2. POST /ingest/upload (FastAPI)
   ↓
3. File processed:
   a. Extract text from PDF/TXT/MD
   b. Split into chunks
   c. Generate embeddings
   d. Prepare for vector database
   ↓
4. POST /ingest (RAG Pipeline)
   ↓
5. Upsert vectors to Endee
   ↓
6. Confirmation returned to UI
```

## 🔧 Configuration Files

### .env Template
```
GEMINI_API_KEY=your_key
ENDEE_URL=http://localhost:8080
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
DEBUG=True
```

### requirements.txt
Core dependencies:
- **fastapi** - Web framework
- **uvicorn** - ASGI server
- **streamlit** - UI framework
- **sentence-transformers** - Embeddings
- **google-generativeai** - Gemini API
- **requests/httpx** - HTTP clients
- **pydantic** - Data validation

### Dockerfile
- Python 3.11 slim base
- Installs dependencies
- Exposes ports 8000 (API), 8501 (UI)
- Health check endpoint
- Default command runs FastAPI

### docker-compose-app.yml
Three services:
1. **endee** - Vector database on :8080
2. **backend** - FastAPI on :8000
3. **frontend** - Streamlit on :8501

## 🚀 Common Tasks

### Adding a New Bot
1. Create `backend/bots/new_bot.py`
2. Implement bot class
3. Add to `rag_pipeline.py`
4. Integrate into workflow

### Adding a New API Endpoint
1. Edit `backend/main.py`
2. Create Pydantic model
3. Implement route function
4. Test with `/docs`

### Changing Embedding Model
1. Edit `backend/config.py`
2. Update `embedding_model` variable
3. Update `embedding_dimension`
4. Model auto-downloads on first use

### Custom Prompts
1. Edit bot files in `backend/bots/`
2. Modify `prompt` variable in functions
3. Test with sample questions

### Adding Document Types
1. Edit `backend/main.py` upload_and_ingest()
2. Add handling for file type
3. Extract text appropriately
4. Rest handles automatically

## 📊 Statistics

| Metric | Value |
|--------|-------|
| Total Files | 30+ |
| Backend Files | 12 |
| Bot Files | 4 |
| Frontend Files | 1 |
| Config/Deploy Files | 5 |
| Documentation Files | 4 |
| Python Lines of Code | 2000+ |
| API Endpoints | 6+ |
| Supported Bot Types | 4 |
| Document Formats | 3 (PDF, TXT, MD) |

## 🔗 Dependencies Map

```
main.py (FastAPI)
├── rag_pipeline.py (RAG orchestration)
│   ├── query_bot.py (Gemini)
│   ├── retrieval_bot.py (Embeddings + Endee)
│   ├── reasoning_bot.py (Gemini)
│   ├── formatter_bot.py (Gemini)
│   └── memory_manager.py (Sessions)
├── config.py (Settings)
├── logging_config.py (Logging)
└── endee_client.py (Vector DB)

streamlit_app.py (Frontend)
└── HTTP calls to main.py

ingest_documents.py (Script)
└── HTTP calls to main.py

Each bot:
├── gemini_client.py
├── endee_client.py
├── embeddings.py
└── logging_config.py
```

## 🎯 Quick Navigation

### I want to...

- **Get started quickly** → Read `QUICKSTART.md`
- **Understand the system** → Read `AI_KNOWLEDGE_ASSISTANT_README.md`
- **Modify/extend the code** → Read `DEVELOPMENT.md`
- **See all files** → You're reading `PROJECT_STRUCTURE.md`
- **Upload documents** → Use Streamlit UI at http://localhost:8501
- **Ask questions** → Use chat interface in Streamlit
- **Test API** → Visit http://localhost:8000/docs
- **View logs** → Check `logs/` directory
- **Ingest sample docs** → Run `python -m scripts.ingest_documents --mode sample`

## 📞 Support Resources

- **Endee Vector DB**: https://github.com/endee-io/endee
- **FastAPI**: https://fastapi.tiangolo.com/
- **Streamlit**: https://docs.streamlit.io/
- **SentenceTransformers**: https://www.sbert.net/
- **Google Gemini**: https://ai.google.dev/

---

**Last Updated**: March 2026
