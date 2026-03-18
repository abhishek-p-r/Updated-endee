# Development Guide

## Project Structure

```
endee-ai-knowledge-assistant/
├── backend/                    # FastAPI backend
│   ├── main.py                # API routes and server setup
│   ├── config.py              # Configuration and settings
│   ├── rag_pipeline.py        # RAG orchestration logic
│   ├── embeddings.py          # Embedding service
│   ├── endee_client.py        # Endee HTTP client
│   ├── gemini_client.py       # Gemini AI integration
│   ├── memory_manager.py      # Conversation memory
│   ├── logging_config.py      # Logging setup
│   └── bots/                  # AI agents
│       ├── query_bot.py       # Query understanding
│       ├── retrieval_bot.py   # Document retrieval
│       ├── reasoning_bot.py   # Answer generation
│       └── formatter_bot.py   # Response formatting
├── frontend/                  # Streamlit UI
│   └── streamlit_app.py       # Web interface
├── scripts/                   # Utility scripts
│   └── ingest_documents.py    # Document ingestion
├── data/                      # Data storage
├── logs/                      # Application logs
├── requirements.txt           # Python dependencies
├── .env.example              # Environment template
├── Dockerfile                # Container image
└── docker-compose-app.yml   # Multi-service setup
```

## Key Components

### RAG Pipeline (`backend/rag_pipeline.py`)

The RAGPipeline orchestrates the complete workflow:

```python
# Process a user query
result = await pipeline.process_query(
    question="What is RAG?",
    session_id="user_123",
    use_conversation_history=True
)
```

**Steps:**
1. Query Understanding - Optimizes the question
2. Knowledge Retrieval - Searches vector database
3. Context Assembly - Formats retrieved documents
4. Answer Generation - Uses Gemini to create response
5. Response Formatting - Structures the output

### AI Bots

#### Query Bot
- Analyzes user intent
- Removes query noise
- Optimizes for semantic search
- Extracts keywords

#### Retrieval Bot
- Generates query embeddings
- Searches Endee vector database
- Formats retrieved documents
- Supports filtered retrieval

#### Reasoning Bot
- Combines context and question
- Uses Gemini for generation
- Incorporates conversation history
- Generates detailed answers

#### Formatter Bot
- Improves text readability
- Extracts key points
- Highlights insights
- Adds source attribution

### Services

#### Embedding Service
- Uses SentenceTransformers
- Generates embeddings for documents and queries
- Batch processing support
- Cached model loading

#### Endee Client
- HTTP API client for vector database
- Collection management
- Vector upsert operations
- Similarity search

#### Gemini Client
- Google Gemini API integration
- Text generation
- Configurable temperature
- Error handling

#### Memory Manager
- Conversation history tracking
- Session-based storage
- Message serialization
- History clearing

## API Endpoints

### Health Check
```
GET /health
```
Returns server status and Endee connection status.

### Ask Question
```
POST /ask
{
  "question": "string",
  "session_id": "string",
  "use_conversation_history": boolean
}
```

### Ingest Documents
```
POST /ingest
{
  "documents": [
    {"text": "string", "source": "string"}
  ],
  "chunk_size": number,
  "chunk_overlap": number
}
```

### Upload File
```
POST /ingest/upload
Content-Type: multipart/form-data
file: <file>
source: optional
```

### Chat History
```
GET /chat/history/{session_id}
DELETE /chat/history/{session_id}
```

## Configuration

### Environment Variables

```env
# Gemini API
GEMINI_API_KEY=your_key_here

# Vector Database
ENDEE_URL=http://localhost:8080

# Server
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
DEBUG=True

# RAG Settings
CHUNK_SIZE=500
CHUNK_OVERLAP=50
MAX_RETRIEVED_DOCUMENTS=5
SIMILARITY_THRESHOLD=0.3
```

### Settings Class

Edit `backend/config.py` to modify defaults:

```python
class Settings(BaseSettings):
    server_host: str = "0.0.0.0"
    server_port: int = 8000
    endee_url: str = "http://localhost:8080"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    chunk_size: int = 500
    max_retrieved_documents: int = 5
```

## Running Locally

### Manual Setup

```bash
# 1. Start Endee
cd endee && ./run.sh

# 2. In new terminal, setup project
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Configure
cp .env.example .env
# Edit .env with GEMINI_API_KEY

# 4. Start backend
python -m uvicorn backend.main:app --reload

# 5. In another terminal, start frontend
streamlit run frontend/streamlit_app.py

# 6. Ingest sample documents
python -m scripts.ingest_documents --mode sample
```

### Using Startup Script

```bash
chmod +x start.sh
./start.sh
```

### Using Docker

```bash
# Start all services
docker-compose -f docker-compose-app.yml up

# Logs
docker-compose -f docker-compose-app.yml logs -f

# Stop
docker-compose -f docker-compose-app.yml down
```

## Testing

### Manual API Testing

```bash
# Health check
curl http://localhost:8000/health

# Ask question
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is a vector database?",
    "session_id": "test_user"
  }'

# Ingest documents
curl -X POST http://localhost:8000/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "documents": [
      {
        "text": "Your document text here",
        "source": "Test Document"
      }
    ]
  }'
```

### With Python

```python
import requests
import asyncio

# Synchronous
response = requests.post(
    "http://localhost:8000/ask",
    json={"question": "What is RAG?"}
)
print(response.json())

# Or use the backend directly
from backend.rag_pipeline import get_rag_pipeline

async def test():
    pipeline = get_rag_pipeline()
    result = await pipeline.process_query("What is RAG?")
    print(result)

asyncio.run(test())
```

## Adding New Features

### Adding a New Bot

1. Create file in `backend/bots/new_bot.py`
2. Inherit from base pattern
3. Implement required methods
4. Add to RAG pipeline

Example:
```python
# backend/bots/summary_bot.py
class SummaryBot:
    def __init__(self):
        self.gemini = get_gemini_client()
    
    def summarize(self, text: str) -> str:
        """Summarize the provided text."""
        prompt = f"Summarize: {text}"
        return self.gemini.generate(prompt)
```

### Adding a New API Endpoint

1. Edit `backend/main.py`
2. Create Pydantic model for request
3. Implement route function
4. Document in API docs

Example:
```python
from pydantic import BaseModel

class SummarizeRequest(BaseModel):
    text: str

@app.post("/summarize")
async def summarize(request: SummarizeRequest):
    # Implementation
    return {"summary": "..."}
```

### Custom Embedding Models

Edit `backend/config.py`:
```python
# Change embedding model
embedding_model: str = "all-mpnet-base-v2"

# Update dimension accordingly
embedding_dimension: int = 768  # For all-mpnet
```

Or use different providers:
- OpenAI: `text-embedding-3-small`
- Cohere: `embed-english-v3.0`
- Hugging Face: Any model on HF

## Performance Optimization

### Embedding Caching
```python
# Cache embeddings for repeated queries
@lru_cache(maxsize=1000)
def cached_embedding(text: str) -> List[float]:
    return embedding_service.generate_embedding(text)
```

### Batch Processing
```python
# Ingest many documents efficiently
documents = [...]  # 1000+ docs
result = await pipeline.ingest_documents(documents)
```

### Connection Pooling
Already implemented with `httpx.AsyncClient`. Customize:
```python
async with httpx.AsyncClient(
    limits=httpx.Limits(
        max_connections=100,
        max_keepalive_connections=20
    )
) as client:
    response = await client.get(url)
```

## Debugging

### Enable Debug Mode

In `.env`:
```
DEBUG=True
```

### View Logs

```bash
# Tail logs in real-time
tail -f logs/app_*.log

# Or check specific date
cat logs/app_20260316.log
```

### Debug Endpoint

Add to `backend/main.py`:
```python
@app.get("/debug/config")
async def debug_config():
    return {
        "settings": settings.__dict__,
        "endee_url": settings.endee_url,
        "embedding_model": settings.embedding_model
    }
```

### Print Debugging

Use console.log style debugging:
```python
logger.debug(f"[DEBUG] Variable value: {value}")
```

## Deployment

### Production Checklist

- [ ] Set DEBUG=False
- [ ] Configure CORS properly
- [ ] Add rate limiting
- [ ] Use environment-specific configs
- [ ] Enable SSL/HTTPS
- [ ] Setup monitoring/logging
- [ ] Configure backup strategy
- [ ] Load testing

### Production Settings

```env
DEBUG=False
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
GEMINI_API_KEY=prod_key_here
ENDEE_URL=https://endee.yourdomain.com
```

### Scaling

1. **Multiple Backend Instances**: Use load balancer (nginx, HAProxy)
2. **Endee Clustering**: Configure Endee for distributed deployment
3. **Caching Layer**: Add Redis for response caching
4. **Database Sharding**: Distribute documents across multiple Endee instances

## Contributing

### Code Style

- Follow PEP 8
- Use type hints
- Document functions with docstrings
- Add logging for important operations

### Testing

- Write tests for new features
- Test error cases
- Verify API contracts
- Performance test large ingestions

### Documentation

- Update README for user-facing changes
- Update this file for developer changes
- Document new endpoints in API
- Add inline comments for complex logic

## Troubleshooting

### Common Issues

**Issue**: `ConnectionError: Endee not responding`
- **Solution**: Ensure Endee is running on localhost:8080

**Issue**: `GEMINI_API_KEY not set`
- **Solution**: Copy .env.example to .env and set your API key

**Issue**: `Embedding model download fails`
- **Solution**: Check internet connection, disk space

**Issue**: `Memory usage growing`
- **Solution**: Check conversation history limits, clear old sessions

**Issue**: `Slow similarity search`
- **Solution**: Adjust chunk_size, reduce max_retrieved_documents, rebuild indexes

## Resources

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Streamlit Docs](https://docs.streamlit.io/)
- [Endee Repo](https://github.com/endee-io/endee)
- [SentenceTransformers](https://www.sbert.net/)
- [Google Gemini API](https://ai.google.dev/)

---

Last Updated: March 2026
