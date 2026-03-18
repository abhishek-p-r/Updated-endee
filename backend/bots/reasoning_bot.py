"""Reasoning and Answer Generation Bot - generates AI answers using Gemini."""
from typing import Optional
from backend.gemini_client import get_gemini_client
from backend.logging_config import get_logger

logger = get_logger("reasoning_bot")


class ReasoningAndAnswerBot:
    """Bot for reasoning over context and generating answers."""
    
    def __init__(self):
        """Initialize the reasoning bot."""
        self.gemini = get_gemini_client()
        logger.info("Initialized Reasoning and Answer Bot")
    
    def generate_answer(
        self,
        question: str,
        context: str,
        conversation_history: str = None
    ) -> Optional[str]:
        """Generate an answer based on context and question.
        
        Args:
            question: The user's question.
            context: Retrieved knowledge context.
            conversation_history: Previous conversation for context.
            
        Returns:
            Generated answer or None if generation fails.
        """
        try:
            conversation_part = (
                "Previous Conversation:\n" + conversation_history + "\n"
                if conversation_history
                else ""
            )
            
            prompt = f"""You are an intelligent AI assistant specialized in answering questions based on provided knowledge.

Your tasks:
1. Analyze the user's question
2. Use the provided context to formulate an accurate answer
3. Combine context and perform logical reasoning
4. Generate a clear and helpful response
5. If the context doesn't contain relevant information, say so clearly

{conversation_part}
Context Information:
{context}

User Question:
{question}

Please provide a comprehensive and accurate answer based on the context. If you need to make any assumptions, state them clearly. Focus on being helpful and accurate."""
            
            response = self.gemini.generate(prompt, temperature=0.7)
            
            if response:
                logger.info("Successfully generated answer")
                return response
            else:
                logger.warning("Failed to generate answer with Gemini")
                return None
        
        except Exception as e:
            logger.error(f"Error generating answer: {str(e)}")
            return None
    
    def generate_summary(self, text: str, max_length: int = 200) -> Optional[str]:
        """Generate a summary of the provided text.
        
        Args:
            text: The text to summarize.
            max_length: Maximum length of the summary.
            
        Returns:
            Summary of the text or None if generation fails.
        """
        try:
            prompt = f"""Please provide a concise summary of the following text in approximately {max_length} characters:

{text}

Summary:"""
            
            response = self.gemini.generate(prompt, temperature=0.5)
            
            if response:
                logger.info("Successfully generated summary")
                return response
            else:
                return None
        
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            return None
