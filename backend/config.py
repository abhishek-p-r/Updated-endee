"""Configuration management for the Endee AI Knowledge Assistant."""
import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    """Application settings."""
    
    # API Configuration
    server_host: str = os.getenv("SERVER_HOST", "0.0.0.0")
    server_port: int = int(os.getenv("SERVER_PORT", "8000"))
    debug: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    # OpenAI Configuration
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    openai_embedding_model: str = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
    
    # Endee Vector Database
    endee_url: str = os.getenv("ENDEE_URL", "http://localhost:8080")
    endee_db_name: str = os.getenv("ENDEE_DB_NAME", "knowledge_base")
    endee_vector_dimension: int = int(os.getenv("ENDEE_VECTOR_DIMENSION", "1536"))
    endee_collection_name: str = "knowledge-base"
    
    # Gemini AI
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    
    # Embedding Model
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_dimension: int = 384
    
    # Backend Configuration
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8000"))
    api_url: str = os.getenv("API_URL", "http://localhost:8000")
    env: str = os.getenv("ENV", "development")
    
    # Frontend Configuration
    frontend_url: str = os.getenv("FRONTEND_URL", "http://localhost:8501")
    
    # Data & File Configuration
    data_dir: str = os.getenv("DATA_DIR", "./data")
    upload_dir: str = os.getenv("UPLOAD_DIR", "./uploads")
    
    # RAG Configuration
    rag_top_k: int = int(os.getenv("RAG_TOP_K", "5"))
    rag_score_threshold: float = float(os.getenv("RAG_SCORE_THRESHOLD", "0.5"))
    rag_temperature: float = float(os.getenv("RAG_TEMPERATURE", "0.7"))
    rag_max_tokens: int = int(os.getenv("RAG_MAX_TOKENS", "1000"))
    
    # Document Processing
    chunk_size: int = int(os.getenv("CHUNK_SIZE", "512"))
    chunk_overlap: int = int(os.getenv("CHUNK_OVERLAP", "50"))
    
    # Standard RAG Configuration
    max_retrieved_documents: int = 5
    similarity_threshold: float = 0.3
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "allow"


settings = Settings()
