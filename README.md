# Endee RAG System - AI-Powered Knowledge Assistant

A production-ready Retrieval-Augmented Generation (RAG) system that combines **Endee vector database** with **OpenAI's GPT-4o-mini** for intelligent document processing and question answering.

## Table of Contents

1. [Quick Overview](#quick-overview)
2. [System Architecture](#system-architecture)
3. [Prerequisites & Requirements](#prerequisites--requirements)
4. [Installation - Step by Step](#installation---step-by-step)
5. [Running the Application - Step by Step](#running-the-application---step-by-step)
6. [Using the Application](#using-the-application)
7. [API Reference](#api-reference)
8. [Project Structure](#project-structure)
9. [Troubleshooting](#troubleshooting)
10. [Performance Tips](#performance-tips)

---

## Quick Overview

This system allows you to:
- Upload documents (PDF, TXT, Markdown)
- Automatically convert them to vector embeddings
- Store embeddings in Endee vector database
- Ask questions and get AI-powered answers with sources
- Access via web interface or REST API

---

## System Architecture

```
┌─────────────────────────────────────────────────┐
│         User Interface (Port 8501)              │
│  ┌──────────────────────────────────────────┐  │
│  │ Streamlit Web UI                         │  │
│  │ - Chat Interface                         │  │
│  │ - Document Upload                        │  │
│  │ - Search                                 │  │
│  │ - Analytics                              │  │
│  └──────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────┐
│      FastAPI Backend (Port 8000)                │
│  ┌──────────────────────────────────────────┐  │
│  │ API Routes & Business Logic              │  │
│  │ - /api/documents/upload                  │  │
│  │ - /api/query/ask                         │  │
│  │ - /api/search                            │  │
│  │ - /api/stats                             │  │
│  └──────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
        ↓              ↓              ↓
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ OpenAI       │  │ Endee Vector │  │ Cache        │
│ Embeddings   │  │ Database     │  │ Manager      │
│ & LLM        │  │ (Port 8001)  │  │              │
└──────────────┘  └──────────────┘  └──────────────┘
```

---

## Prerequisites & Requirements

### System Requirements
- Python 3.9 or higher
- 4GB RAM minimum (8GB recommended)
- Docker (optional but recommended)
- Internet connection for API calls

### API Keys Required
1. **OpenAI API Key** (for GPT-4o-mini and embeddings)
   - Get it: https://platform.openai.com/api-keys
   - Cost: Pay-as-you-go (embeddings ~$0.02/1M tokens)

2. **Endee Vector Database** (local or cloud)
   - Self-hosted: Free open-source
   - Cloud: https://www.endee.io/

---

## Installation - Step by Step

### Step 1: Clone the Repository

```bash
git clone https://github.com/abhishek-p-r/endee.git
cd endee
git checkout endee-ai-assistant
```

### Step 2: Create and Activate Python Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### Step 3: Install All Dependencies

```bash
# Install required Python packages
pip install -r requirements.txt

# Verify installation
pip list | grep -E "openai|fastapi|streamlit"
```

### Step 4: Get Your OpenAI API Key

**Steps:**
1. Go to https://platform.openai.com/api-keys
2. Click "Create new secret key"
3. Copy the key (starts with `sk-`)
4. Save it somewhere safe

### Step 5: Set Up Endee Vector Database

**Option A: Using Docker (Easiest - Recommended)**

```bash
# Pull and run Endee Docker image
docker run -d -p 8001:8001 --name endee-db endeeio/endee:latest

# Verify it's running
curl http://localhost:8001/health

# Expected response: {"status": "healthy"}
```

**Option B: Manual Installation (Linux/macOS)**

```bash
# Clone Endee repository
git clone https://github.com/endeeio/endee.git
cd endee

# Install and build
chmod +x install.sh
./install.sh --release --avx2

# Run the server
./endee --port 8001

# Verify: curl http://localhost:8001/health
```

**Option C: Using Docker Compose (All services together)**

```bash
# Skip to "Running the Application" section below
```

### Step 6: Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit the file with your settings
nano .env
# Or use your preferred text editor
```

**Add these values to `.env`:**

```env
# OpenAI Configuration
OPENAI_API_KEY=sk-your-key-here
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
OPENAI_LLM_MODEL=gpt-4o-mini

# Endee Configuration
ENDEE_URL=http://localhost:8001
ENDEE_API_KEY=optional-key

# Server Configuration
API_HOST=0.0.0.0
API_PORT=8000
STREAMLIT_PORT=8501

# Logging
LOG_LEVEL=INFO
```

### Step 7: Verify Installation

```bash
# Test that everything is set up correctly
python scripts/verify_setup.py

# Expected output:
# ✓ Python version OK
# ✓ Dependencies installed
# ✓ Environment variables set
# ✓ Endee reachable
# ✓ OpenAI API key valid
```

---

## Running the Application - Step by Step

### Option 1: Docker Compose (Easiest - Recommended)

This runs all services in one command with automatic startup.

```bash
# Step 1: Navigate to project directory
cd /path/to/endee

# Step 2: Start all services
docker-compose up -d

# Step 3: Wait for services to initialize (30 seconds)
sleep 30

# Step 4: Verify all services are running
docker-compose ps

# Expected output:
# NAME              STATUS
# endee-db          Up
# backend           Up  
# frontend          Up

# Step 5: Open services in browser
# Web UI:      http://localhost:8501
# API Docs:    http://localhost:8000/docs
# Endee Health: http://localhost:8001/health

# Step 6: To stop all services
docker-compose down
```

### Option 2: Manual Three-Terminal Setup (Detailed)

Run each component in a separate terminal window.

**Terminal 1: Start Endee Vector Database**

```bash
# Option A: Using Docker
docker run -p 8001:8001 --name endee-db endeeio/endee:latest

# Option B: Using local binary
cd endee
./endee --port 8001

# Wait for: "Server started on port 8001"
# Verify: curl http://localhost:8001/health
```

**Terminal 2: Start FastAPI Backend Server**

```bash
# Navigate to project
cd /path/to/endee

# Activate virtual environment
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate  # Windows

# Start the API server
python -m uvicorn backend.app:app --host 0.0.0.0 --port 8000 --reload

# Wait for: "Uvicorn running on http://0.0.0.0:8000"
# Access API docs: http://localhost:8000/docs
```

**Terminal 3: Start Streamlit Web Interface**

```bash
# In a new terminal, navigate to project
cd /path/to/endee

# Activate virtual environment
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate  # Windows

# Start Streamlit UI
streamlit run frontend/app.py --server.port 8501

# Wait for: "You can now view your Streamlit app"
# Browser will open automatically to http://localhost:8501
```

### Option 3: Using the Startup Script

```bash
# Make script executable
chmod +x start.sh

# Run it
./start.sh

# This will:
# 1. Check all prerequisites
# 2. Start Endee database
# 3. Start FastAPI backend
# 4. Start Streamlit frontend
# 5. Open browser to http://localhost:8501
```

---

## Using the Application

### Web Interface (Easiest Method)

**Step 1: Open the Web Interface**
- Go to http://localhost:8501 in your browser
- You should see the Streamlit app

**Step 2: Upload Documents (First Time)**
- Click "Upload Documents" tab
- Select PDF, TXT, or Markdown files
- Click "Process Documents"
- Wait for "Processing complete" message

**Step 3: Ask Questions**
- Click "Chat" tab
- Type your question in the text box
- Press Enter or click "Send"
- See AI response with sources

**Step 4: Search Documents**
- Click "Search" tab
- Enter a search query
- View semantic search results
- Click on results to see full text

**Step 5: View Analytics**
- Click "Analytics" tab
- See query statistics
- Monitor system performance

### REST API Usage

**Example 1: Upload a Document**

```bash
curl -X POST "http://localhost:8000/api/documents/upload" \
  -F "file=@document.pdf"
```

Response:
```json
{
  "document_id": "doc_123",
  "filename": "document.pdf",
  "chunks": 45,
  "status": "processed"
}
```

**Example 2: Ask a Question**

```bash
curl -X POST "http://localhost:8000/api/query/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is the main topic?",
    "top_k": 5
  }'
```

Response:
```json
{
  "answer": "The main topic is...",
  "sources": [
    {
      "document": "document.pdf",
      "chunk": 12,
      "text": "...",
      "score": 0.95
    }
  ],
  "tokens_used": 450
}
```

**Example 3: Stream Responses**

```bash
curl -X POST "http://localhost:8000/api/query/stream" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is...?"}' \
  --stream
```

**Example 4: Semantic Search**

```bash
curl -X POST "http://localhost:8000/api/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "important information",
    "top_k": 10
  }'
```

**Example 5: Get System Stats**

```bash
curl http://localhost:8000/api/stats
```

Response:
```json
{
  "total_queries": 156,
  "avg_response_time": 2.3,
  "cache_hit_rate": 0.65,
  "documents_stored": 5,
  "vectors_stored": 243
}
```

### Interactive Demo

```bash
# Run the interactive demo
python scripts/demo.py

# This will:
# 1. Create sample documents
# 2. Upload them
# 3. Ask sample questions
# 4. Display results
```

---

## API Reference

### Document Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/documents/upload` | Upload and process documents |
| GET | `/api/documents/list` | List all uploaded documents |
| DELETE | `/api/documents/{doc_id}` | Delete a document |
| GET | `/api/documents/{doc_id}` | Get document details |

### Query & Search

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/query/ask` | Ask question and get answer |
| POST | `/api/query/stream` | Get streaming response |
| POST | `/api/search` | Semantic search in documents |
| POST | `/api/query/optimize` | Optimize and analyze query |

### System

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check status |
| GET | `/api/stats` | System statistics |
| GET | `/api/cache/stats` | Cache statistics |
| POST | `/api/cache/clear` | Clear query cache |

Full interactive documentation available at: **http://localhost:8000/docs**

---

## Project Structure

```
endee/
├── README.md                          # This file (comprehensive guide)
├── requirements.txt                   # All Python dependencies
├── .env.example                       # Environment configuration template
├── docker-compose.yml                 # Multi-container setup
├── start.sh                           # Convenient startup script
│
├── backend/                           # FastAPI Backend (Core Logic)
│   ├── app.py                         # Main FastAPI application (461 lines)
│   │   └── 9 API endpoints for query, search, documents
│   │
│   ├── openai_client.py               # OpenAI integration (425 lines)
│   │   ├── Embeddings (text-embedding-3-small)
│   │   └── LLM completions (gpt-4o-mini)
│   │
│   ├── endee_vector_db.py             # Endee integration (428 lines)
│   │   ├── Vector storage & retrieval
│   │   ├── Semantic search
│   │   └── Collection management
│   │
│   ├── document_processor.py          # Document handling (398 lines)
│   │   ├── Load PDF, TXT, Markdown
│   │   ├── Text chunking with overlap
│   │   └── Metadata extraction
│   │
│   ├── rag_system.py                  # RAG pipeline (402 lines)
│   │   ├── Document embedding
│   │   ├── Semantic search coordination
│   │   └── Answer generation
│   │
│   ├── cache_manager.py               # Query result caching
│   ├── analytics.py                   # Performance metrics
│   ├── query_optimizer.py             # Query optimization
│   ├── config.py                      # Configuration settings
│   ├── logging_config.py              # Logging setup
│   │
│   └── bots/                          # Multi-agent system (if using)
│       ├── query_bot.py               # Query analysis
│       ├── retrieval_bot.py           # Document retrieval
│       ├── reasoning_bot.py           # Answer reasoning
│       └── formatter_bot.py           # Response formatting
│
├── frontend/                          # Streamlit Web Interface
│   └── app.py                         # Main UI (596 lines)
│       ├── Chat tab - Ask questions
│       ├── Upload tab - Upload documents
│       ├── Search tab - Semantic search
│       ├── Analytics tab - View metrics
│       └── Settings tab - Configuration
│
├── scripts/                           # Utility Scripts
│   ├── demo.py                        # Interactive demo (343 lines)
│   ├── verify_setup.py                # System verification (323 lines)
│   ├── test_api.py                    # API testing utility
│   └── ingest_documents.py            # Batch document ingestion
│
├── docs/                              # Additional Documentation
│   ├── getting-started.md             # Quick start guide
│   ├── architecture.md                # System architecture
│   └── contributing.md                # Contribution guidelines
│
└── tests/                             # Test Suite
    └── README.md                      # Testing instructions
```

### Key Files Explained

| File | Purpose | Key Functions |
|------|---------|---------------|
| `backend/app.py` | FastAPI server | All REST endpoints |
| `backend/openai_client.py` | OpenAI integration | Embeddings & LLM |
| `backend/endee_vector_db.py` | Endee integration | Vector storage & search |
| `backend/document_processor.py` | Document handling | Parse & chunk files |
| `backend/rag_system.py` | RAG orchestration | Coordinate all components |
| `frontend/app.py` | Web interface | Multi-tab Streamlit UI |
| `scripts/verify_setup.py` | System verification | Check all components |

---

## Troubleshooting

### Issue 1: "Cannot connect to Endee"

**Error:** `Connection error: http://localhost:8001`

**Solution:**
```bash
# Check if Endee is running
curl http://localhost:8001/health

# If not responding, start Endee
docker run -d -p 8001:8001 endeeio/endee:latest

# Or check if port is in use
lsof -i :8001
```

### Issue 2: "OpenAI API key invalid"

**Error:** `Invalid OpenAI API key`

**Solution:**
```bash
# Verify your key format (should start with sk-)
echo $OPENAI_API_KEY

# If not set, add to .env file
nano .env
# Add: OPENAI_API_KEY=sk-your-actual-key

# Restart backend service
# Press Ctrl+C and re-run the backend command
```

### Issue 3: "Port already in use"

**Error:** `Address already in use: ('0.0.0.0', 8000)`

**Solution:**
```bash
# Find what's using the port
lsof -i :8000  # for backend
lsof -i :8501  # for frontend
lsof -i :8001  # for Endee

# Kill the process
kill -9 <PID>

# Or use different ports
python -m uvicorn backend.app:app --port 8002
streamlit run frontend/app.py --server.port 8502
```

### Issue 4: "Out of memory with large documents"

**Error:** `MemoryError during document processing`

**Solution:**
```bash
# Reduce chunk size in backend config
nano backend/config.py

# Change these values:
CHUNK_SIZE = 500      # reduce from 1000
CHUNK_OVERLAP = 50    # reduce from 100

# Restart the application
```

### Issue 5: "Slow query responses"

**Symptom:** Queries take 10+ seconds

**Solution:**
```bash
# Check cache effectiveness
curl http://localhost:8000/api/cache/stats

# Clear old cache if needed
curl -X POST http://localhost:8000/api/cache/clear

# Check Endee health
curl http://localhost:8001/health

# Monitor system resources
# Ensure 4GB+ RAM available
```

### Issue 6: "No search results"

**Error:** "No relevant documents found"

**Solution:**
```bash
# Verify documents were uploaded
curl http://localhost:8000/api/documents/list

# Check vector database has data
curl http://localhost:8001/health

# Try uploading documents again
# Use clear, well-formatted text files

# Adjust search parameters in web UI
# Increase top_k from 5 to 10
```

### Getting Help

```bash
# 1. Run system verification
python scripts/verify_setup.py

# 2. Check API documentation
open http://localhost:8000/docs

# 3. Run interactive demo
python scripts/demo.py

# 4. Check logs in backend terminal for errors
```

---

## Performance Tips

1. **Optimal Chunk Size**: 500-1000 characters
   - Too small = more vectors, slower search
   - Too large = lost context

2. **Use Caching**: Enabled by default
   - Saves 50-80% on repeated queries

3. **Batch Operations**: Upload multiple documents at once
   - More efficient than single uploads

4. **Search Parameters**: Start with top_k=5
   - Increase only if needed

5. **Monitor Analytics**: Check `/api/stats` regularly
   - Identify bottlenecks

---

## Advanced Configuration

### Custom Embedding Model

Edit `backend/config.py`:
```python
OPENAI_EMBEDDING_MODEL = "text-embedding-3-large"  # Higher quality
```

### Custom LLM Model

Edit `backend/config.py`:
```python
OPENAI_LLM_MODEL = "gpt-4"  # More powerful, slower
```

### Cache Configuration

Edit `backend/cache_manager.py`:
```python
CACHE_TTL = 3600  # Cache for 1 hour
MAX_CACHE_SIZE = 1000  # Store up to 1000 queries
```

### Semantic Search Threshold

Edit `backend/rag_system.py`:
```python
SIMILARITY_THRESHOLD = 0.7  # Minimum relevance score
TOP_K = 5  # Number of results to return
```

---

## Production Deployment

For production use:

1. **Use environment variables** for all secrets
2. **Enable CORS** for cross-domain requests
3. **Set up monitoring** with prometheus/grafana
4. **Use PostgreSQL** instead of SQLite for cache
5. **Deploy with Kubernetes** for scaling
6. **Set up CI/CD** with GitHub Actions

See `DEVELOPMENT.md` for detailed production setup.

---

## Additional Resources

- **API Docs**: http://localhost:8000/docs (Swagger UI)
- **GitHub**: https://github.com/abhishek-p-r/endee
- **Endee Docs**: https://github.com/endeeio/endee
- **OpenAI Docs**: https://platform.openai.com/docs
- **Streamlit Docs**: https://docs.streamlit.io/

---

## License

This project is licensed under the MIT License. See LICENSE file for details.

---

**Last Updated**: March 2026  
**Version**: 2.0 - Complete Rebuild with Endee + OpenAI Integration  
**Status**: Production Ready


