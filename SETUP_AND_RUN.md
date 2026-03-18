# Endee RAG System - Complete Setup and Execution Guide

Complete step-by-step guide to set up and run the Endee RAG system.

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Pre-Installation Checks](#pre-installation-checks)
3. [Installation Steps](#installation-steps)
4. [Running the System](#running-the-system)
5. [Verification](#verification)
6. [First Use](#first-use)
7. [Troubleshooting](#troubleshooting)

## System Requirements

### Hardware

- **CPU**: 4+ cores recommended
- **RAM**: 8GB minimum, 16GB recommended
- **Disk**: 10GB free space

### Software

- **Python**: 3.9 or higher
- **Docker**: (Required for Endee vector database)
- **Git**: (Optional, for cloning repository)

### API Keys

- **OpenAI API Key**: Get from https://platform.openai.com/api-keys
  - Free trial credits available
  - Pricing: ~$0.02 per 1M embedding tokens

## Pre-Installation Checks

### 1. Check Python Installation

```bash
python --version
# Should output: Python 3.9.x or higher
```

If not installed, download from https://www.python.org/downloads/

### 2. Check Docker Installation

```bash
docker --version
# Should output: Docker version 20.x or higher
```

If not installed, download from https://docs.docker.com/get-docker/

### 3. Verify OpenAI API Key

```bash
echo $OPENAI_API_KEY
# Should display your API key (or create one first)
```

## Installation Steps

### Step 1: Clone or Download Repository

```bash
# Option A: Using Git
git clone https://github.com/abhishek-p-r/endee.git
cd endee

# Option B: Download ZIP
# Extract the provided endee.zip file
cd endee
```

### Step 2: Create Python Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### Step 3: Install Python Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

Expected output:
```
Successfully installed fastapi-0.104.1 uvicorn-0.24.0 ...
```

### Step 4: Configure Environment Variables

```bash
# Copy the example file
cp .env.example .env

# Edit .env with your settings
nano .env  # or use your preferred editor
```

Add your configuration:

```bash
# OpenAI Configuration (REQUIRED)
OPENAI_API_KEY=sk-your-api-key-here

# Endee Configuration
ENDEE_HOST=localhost
ENDEE_PORT=8000

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Logging
LOG_LEVEL=INFO
```

### Step 5: Verify Setup

```bash
python scripts/verify_setup.py
```

Expected output:
```
✓ Python version OK
✓ Dependencies installed
✓ Environment variables set
✓ Project structure OK
```

If any checks fail, see the [Troubleshooting](#troubleshooting) section.

## Running the System

### Option 1: Automated Startup (Recommended)

```bash
# Make script executable
chmod +x start.sh

# Run startup script
./start.sh
```

This will:
1. Start Endee vector database
2. Start FastAPI backend
3. Start Streamlit frontend
4. Open browser to http://localhost:8501

### Option 2: Manual Startup (Advanced)

Start each component in a separate terminal:

#### Terminal 1: Start Endee Vector Database

```bash
docker run -p 8000:8000 --name endee-db endeeio/endee:latest
```

Wait for output: `Listening on http://0.0.0.0:8000`

#### Terminal 2: Start FastAPI Backend

```bash
source venv/bin/activate  # Activate virtual environment
python -m uvicorn backend.app:app --host 0.0.0.0 --port 8000 --reload
```

Wait for output: `Uvicorn running on http://0.0.0.0:8000`

#### Terminal 3: Start Streamlit Frontend

```bash
source venv/bin/activate  # Activate virtual environment
streamlit run frontend/app.py
```

Wait for output: `You can now view your Streamlit app in your browser`

### Option 3: Docker Compose

```bash
docker-compose -f docker-compose-app.yml up
```

This starts all services in containers.

## Verification

### Check System Health

```bash
# API health check
curl http://localhost:8000/health

# Expected response:
# {"status":"healthy","endee_connected":true,"openai_configured":true,"rag_ready":true}
```

### Access Web Interface

Open browser and navigate to:

```
http://localhost:8501
```

You should see the Endee RAG System interface.

### Access API Documentation

```
http://localhost:8000/docs        # Swagger UI
http://localhost:8000/redoc       # ReDoc
```

## First Use

### Step 1: Verify Everything Works

```bash
# Run demo script
python scripts/demo.py
```

This will:
1. Create sample documents
2. Ingest them into the database
3. Perform semantic searches
4. Generate AI answers

### Step 2: Upload Your Documents

Using the Web Interface:

1. Go to "Document Upload" tab
2. Click "Upload documents"
3. Select .txt, .pdf, or .md files
4. Wait for ingestion to complete

### Step 3: Ask Questions

Using the Web Interface:

1. Go to "Chat" tab
2. Type your question
3. Click "Send"
4. View the AI answer and sources

Using the REST API:

```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is in my documents?",
    "top_k": 5
  }'
```

## Troubleshooting

### Issue: "Cannot connect to OpenAI"

```
Error: "Invalid API key provided"
```

**Solution:**
```bash
# Check if API key is set
echo $OPENAI_API_KEY

# If empty, set it
export OPENAI_API_KEY="sk-your-key-here"

# Restart the application
```

### Issue: "Endee server not responding"

```
Error: "Cannot connect to http://localhost:8000"
```

**Solution:**
```bash
# Check if Endee is running
docker ps

# If not running, start it
docker run -p 8000:8000 endeeio/endee:latest

# If port already in use, stop other container
docker stop endee-db
docker rm endee-db
```

### Issue: "Python dependencies not found"

```
ModuleNotFoundError: No module named 'fastapi'
```

**Solution:**
```bash
# Activate virtual environment
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: "Port already in use"

```
Address already in use
```

**Solution:**
```bash
# Find process using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or use a different port
python -m uvicorn backend.app:app --port 8001
```

### Issue: "Streamlit connection error"

```
Cannot connect to API server
```

**Solution:**
```bash
# Check API is running
curl http://localhost:8000/health

# Check firewall settings
# May need to allow port 8000 through firewall

# Restart API
# Terminal 2: Ctrl+C then re-run uvicorn command
```

### Issue: "Rate limit exceeded"

```
Error: RateLimitError: Rate limit exceeded
```

**Solution:**
```bash
# Wait 60 seconds
# Retry the request

# Or reduce request frequency
```

## Performance Tips

### For Large Document Collections

1. **Batch Process Documents**
   ```python
   # Process multiple files at once
   result = await rag_system.ingest_documents([
       "doc1.txt", "doc2.pdf", "doc3.md"
   ])
   ```

2. **Adjust Chunking**
   ```python
   processor = DocumentProcessor(
       chunk_size=1000,     # Larger chunks for speed
       chunk_overlap=100
   )
   ```

3. **Filter Metadata**
   ```python
   results = await endee_db.search(
       query_embedding=emb,
       metadata_filter={"file_type": "pdf"}
   )
   ```

### For Real-Time Responses

1. **Use Streaming**
   ```python
   async for chunk in rag_system.stream_answer(query):
       # Update UI in real-time
   ```

2. **Reduce Search Results**
   ```python
   top_k = 3  # Search fewer results
   ```

3. **Cache Results**
   ```python
   # Results are automatically cached
   # Repeat queries are faster
   ```

## Next Steps

After successful setup:

1. **Read Documentation**
   - See `README_ENDEE_RAG.md` for complete documentation
   - See `API_REFERENCE.md` for API details

2. **Try Examples**
   - Run `python scripts/demo.py` for interactive demo
   - Check Jupyter notebooks in `notebooks/`

3. **Integrate with Your Application**
   - Use the REST API from any application
   - Or import Python modules directly

4. **Deploy to Production**
   - See Docker deployment guide
   - Configure for your infrastructure

## Support

If you encounter issues:

1. **Check Troubleshooting Guide** (above)
2. **Run Setup Verification**: `python scripts/verify_setup.py`
3. **Check Logs**: Look in the terminal output
4. **Review Documentation**: See `README_ENDEE_RAG.md`

## Environment Variables Reference

```bash
# Required
OPENAI_API_KEY=sk-...              # OpenAI API key

# Optional (defaults shown)
ENDEE_HOST=localhost               # Endee server host
ENDEE_PORT=8000                    # Endee server port
API_HOST=0.0.0.0                   # API bind address
API_PORT=8000                      # API port
LOG_LEVEL=INFO                     # Logging level
```

## Quick Reference Commands

```bash
# Setup
python -m venv venv
source venv/bin/activate           # Linux/Mac
pip install -r requirements.txt

# Run
./start.sh                          # Automated
# OR
docker run -p 8000:8000 endeeio/endee:latest  # Terminal 1
python -m uvicorn backend.app:app             # Terminal 2
streamlit run frontend/app.py                 # Terminal 3

# Verify
python scripts/verify_setup.py      # Check setup
python scripts/demo.py              # Run demo

# Test
curl http://localhost:8000/health   # API health
curl http://localhost:8000/docs     # API docs

# Stop
Ctrl+C in each terminal
docker stop endee-db
```

## Success Indicators

Your setup is complete when you see:

- [x] Python dependencies installed
- [x] Environment variables configured
- [x] Endee server running on localhost:8000
- [x] API server running on localhost:8000
- [x] Streamlit UI accessible at localhost:8501
- [x] Demo script runs successfully
- [x] Documents can be uploaded
- [x] Questions can be answered
- [x] API returns results

Congratulations! You're ready to use the Endee RAG System.
