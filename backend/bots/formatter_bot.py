"""Response Formatting Bot - formats and structures the final output."""
from typing import Dict, Any, Optional
from backend.gemini_client import get_gemini_client
from backend.logging_config import get_logger

logger = get_logger("formatter_bot")


class ResponseFormattingBot:
    """Bot for formatting and structuring the final response."""
    
    def __init__(self):
        """Initialize the formatter bot."""
        self.gemini = get_gemini_client()
        logger.info("Initialized Response Formatting Bot")
    
    def format_response(self, answer: str, sources: list = None) -> Dict[str, Any]:
        """Format the final response with additional structure.
        
        Args:
            answer: The generated answer.
            sources: List of sources used.
            
        Returns:
            Formatted response dictionary.
        """
        try:
            formatted = {
                "answer": answer,
                "sources": sources or [],
                "formatted_text": self._improve_readability(answer),
                "key_points": self._extract_key_points(answer)
            }
            
            logger.info("Successfully formatted response")
            return formatted
        
        except Exception as e:
            logger.error(f"Error formatting response: {str(e)}")
            return {
                "answer": answer,
                "sources": sources or [],
                "formatted_text": answer,
                "key_points": []
            }
    
    def _improve_readability(self, text: str) -> str:
        """Improve the readability of the text.
        
        Args:
            text: The text to improve.
            
        Returns:
            More readable version of the text.
        """
        # Add bullet points for list items
        lines = text.split('\n')
        formatted_lines = []
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('-') and not line.startswith('•'):
                # Check if it looks like a list item
                if any(c in line for c in [':', ';']) and len(line) > 10:
                    formatted_lines.append(f"• {line}")
                else:
                    formatted_lines.append(line)
            else:
                formatted_lines.append(line)
        
        return '\n'.join(formatted_lines)
    
    def _extract_key_points(self, text: str) -> list:
        """Extract key points from the text.
        
        Args:
            text: The text to analyze.
            
        Returns:
            List of key points.
        """
        key_points = []
        
        # Look for sentences with keywords
        keywords = ['important', 'key', 'critical', 'essential', 'main', 'primary']
        sentences = text.split('.')
        
        for sentence in sentences:
            sentence = sentence.strip()
            if any(keyword in sentence.lower() for keyword in keywords):
                if sentence and len(sentence) > 10:
                    key_points.append(sentence)
        
        return key_points[:5]  # Return top 5 key points
    
    def highlight_important_insights(
        self,
        answer: str,
        max_insights: int = 3
    ) -> Dict[str, Any]:
        """Highlight the most important insights from the answer.
        
        Args:
            answer: The answer text.
            max_insights: Maximum number of insights to highlight.
            
        Returns:
            Dictionary with highlighted insights.
        """
        try:
            prompt = f"""Extract the {max_insights} most important insights from the following text:

{answer}

Format your response as a numbered list with each insight on a new line."""
            
            response = self.gemini.generate(prompt, temperature=0.5)
            
            if response:
                insights = [line.strip() for line in response.split('\n') if line.strip()]
                logger.info(f"Highlighted {len(insights)} insights")
                return {
                    "success": True,
                    "insights": insights
                }
            else:
                return {"success": False, "insights": []}
        
        except Exception as e:
            logger.error(f"Error highlighting insights: {str(e)}")
            return {"success": False, "insights": []}
