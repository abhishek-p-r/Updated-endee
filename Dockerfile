FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements_new.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements_new.txt

# Copy application code
COPY backend_v2/ ./backend_v2/
COPY frontend_v2/ ./frontend_v2/
COPY .env.example .env

# Create necessary directories
RUN mkdir -p logs data uploads

# Expose ports
EXPOSE 8000 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command (starts backend)
CMD ["python", "-m", "backend_v2.main"]
