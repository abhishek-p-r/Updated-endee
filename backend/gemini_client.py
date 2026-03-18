"""Client for Google Gemini API."""
import os
from typing import Optional

try:
    import google.generativeai as genai
except ImportError:
    raise ImportError("Install with: pip install google-generativeai")

from backend.config import settings
from backend.logging_config import get_logger

logger = get_logger("gemini_client")


class GeminiClient:
    """Client for Google Gemini API."""
    
    def __init__(self, api_key: str = None):
        self.api_key = (
            api_key 
            or os.getenv("GEMINI_API_KEY") 
            or settings.gemini_api_key
        )
        
        if not self.api_key:
            logger.warning("No Gemini API key provided")
            self.model = None
        else:
            try:
                genai.configure(api_key=self.api_key)

                # Use stable model
                self.model = genai.GenerativeModel("gemini-pro")

                logger.info("Gemini client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini: {str(e)}")
                self.model = None
    
    def generate_response(self, query: str, context: str = "") -> Optional[str]:
        if not self.model:
            logger.error("Gemini model not initialized")
            return None
            
        prompt = f"""
You are Endee AI Assistant.

Context:
{context}

Question:
{query}
"""

        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Error generating with Gemini: {str(e)}")
            return None
            
    async def generate_response_async(self, query: str, context: str = "") -> Optional[str]:
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.generate_response, query, context)


# Singleton
_gemini_client = None

def get_gemini_client() -> GeminiClient:
    global _gemini_client
    if _gemini_client is None:
        _gemini_client = GeminiClient()
    return _gemini_client