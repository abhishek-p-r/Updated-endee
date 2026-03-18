"""Query Understanding Bot - analyzes and improves user questions."""
from typing import Dict
from backend.gemini_client import get_gemini_client
from backend.logging_config import get_logger

logger = get_logger("query_bot")


class QueryUnderstandingBot:
    """Bot for understanding and optimizing user queries."""
    
    def __init__(self):
        """Initialize the query understanding bot."""
        self.gemini = get_gemini_client()
        logger.info("Initialized Query Understanding Bot")
    
    def analyze_query(self, user_question: str) -> Dict[str, str]:
        """Analyze and improve the user's question.
        
        Args:
            user_question: The original user question.
            
        Returns:
            Dictionary with original and optimized queries.
        """
        try:
            prompt = f"""You are a query optimization expert. 
            
Analyze the following user question and:
1. Identify the main intent
2. Remove any noise or irrelevant parts
3. Optimize it for semantic search

User Question: "{user_question}"

Provide a response in this format:
INTENT: [detected intent]
OPTIMIZED_QUERY: [optimized version for search]
KEYWORDS: [key terms separated by commas]"""
            
            response = self.gemini.generate(prompt, temperature=0.3)
            
            if not response:
                logger.warning("Failed to analyze query with Gemini")
                return {
                    "original": user_question,
                    "optimized": user_question,
                    "intent": "general",
                    "keywords": []
                }
            
            # Parse response
            lines = response.strip().split('\n')
            result = {
                "original": user_question,
                "optimized": user_question,
                "intent": "general",
                "keywords": []
            }
            
            for line in lines:
                if line.startswith("INTENT:"):
                    result["intent"] = line.replace("INTENT:", "").strip()
                elif line.startswith("OPTIMIZED_QUERY:"):
                    result["optimized"] = line.replace("OPTIMIZED_QUERY:", "").strip()
                elif line.startswith("KEYWORDS:"):
                    keywords = line.replace("KEYWORDS:", "").strip()
                    result["keywords"] = [k.strip() for k in keywords.split(",")]
            
            logger.info(f"Query analyzed: {result['optimized']}")
            return result
        
        except Exception as e:
            logger.error(f"Error analyzing query: {str(e)}")
            return {
                "original": user_question,
                "optimized": user_question,
                "intent": "general",
                "keywords": []
            }

