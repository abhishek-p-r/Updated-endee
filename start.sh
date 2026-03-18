#!/bin/bash

# Endee AI Knowledge Assistant - Startup Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Endee AI Knowledge Assistant - Multi-Agent RAG   ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════╝${NC}"
echo ""

# Check Python version
echo -e "${YELLOW}Checking Python version...${NC}"
python_version=$(python --version 2>&1 | awk '{print $2}')
echo -e "${GREEN}✓ Python ${python_version}${NC}"
echo ""

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${GREEN}✓ Virtual environment exists${NC}"
fi
echo ""

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source venv/bin/activate
echo -e "${GREEN}✓ Virtual environment activated${NC}"
echo ""

# Install dependencies
echo -e "${YELLOW}Installing dependencies...${NC}"
pip install -q -r requirements.txt
echo -e "${GREEN}✓ Dependencies installed${NC}"
echo ""

# Check environment file
echo -e "${YELLOW}Checking environment configuration...${NC}"
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠ .env file not found!${NC}"
    echo -e "${YELLOW}Creating .env from template...${NC}"
    cp .env.example .env
    echo -e "${YELLOW}⚠ Please edit .env with your GEMINI_API_KEY${NC}"
    echo ""
else
    echo -e "${GREEN}✓ .env file found${NC}"
fi
echo ""

# Create necessary directories
echo -e "${YELLOW}Creating necessary directories...${NC}"
mkdir -p logs data/knowledge_base
echo -e "${GREEN}✓ Directories created${NC}"
echo ""

# Check Endee connection
echo -e "${YELLOW}Checking Endee Vector Database...${NC}"
if curl -s http://localhost:8080/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Endee is running on http://localhost:8080${NC}"
else
    echo -e "${RED}✗ Endee is not running!${NC}"
    echo -e "${YELLOW}Please start Endee with:${NC}"
    echo -e "${BLUE}  cd endee && ./run.sh${NC}"
    echo ""
fi
echo ""

# Display startup instructions
echo -e "${BLUE}╔════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║           Starting Services                       ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}Starting in background...${NC}"
echo ""

# Create a cleanup function
cleanup() {
    echo ""
    echo -e "${YELLOW}Shutting down services...${NC}"
    kill $backend_pid 2>/dev/null || true
    kill $frontend_pid 2>/dev/null || true
    echo -e "${GREEN}✓ Services stopped${NC}"
    exit 0
}

# Set trap to cleanup on exit
trap cleanup EXIT INT TERM

# Start backend
echo -e "${YELLOW}Starting FastAPI Backend...${NC}"
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000 &
backend_pid=$!
echo -e "${GREEN}✓ Backend started (PID: $backend_pid)${NC}"
sleep 2

# Start frontend
echo -e "${YELLOW}Starting Streamlit Frontend...${NC}"
streamlit run frontend/streamlit_app.py --server.port 8501 --server.address 0.0.0.0 &
frontend_pid=$!
echo -e "${GREEN}✓ Frontend started (PID: $frontend_pid)${NC}"
sleep 3

echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║           Services Running                        ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}✓ Backend API${NC}       : http://localhost:8000"
echo -e "${GREEN}  - Docs       : http://localhost:8000/docs${NC}"
echo -e "${GREEN}  - ReDoc      : http://localhost:8000/redoc${NC}"
echo ""
echo -e "${GREEN}✓ Frontend UI${NC}      : http://localhost:8501"
echo ""
echo -e "${GREEN}✓ Endee Database${NC}   : http://localhost:8080"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop all services${NC}"
echo ""

# Ingest sample documents automatically
read -p "Would you like to ingest sample documents? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Ingesting sample documents...${NC}"
    python -m scripts.ingest_documents --mode sample
    echo ""
fi

# Keep script running
wait

