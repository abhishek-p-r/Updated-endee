"""Chat memory and conversation history management."""
from typing import List, Dict, Any
from datetime import datetime
from backend.logging_config import get_logger

logger = get_logger("memory_manager")


class Message:
    """Represents a single message in the conversation."""
    
    def __init__(self, role: str, content: str, timestamp: datetime = None):
        """Initialize a message.
        
        Args:
            role: Either 'user' or 'assistant'.
            content: The message content.
            timestamp: When the message was created.
        """
        self.role = role
        self.content = content
        self.timestamp = timestamp or datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary."""
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat()
        }


class ConversationMemory:
    """Manages conversation history and context."""
    
    def __init__(self, max_history: int = 10):
        """Initialize conversation memory.
        
        Args:
            max_history: Maximum number of messages to keep.
        """
        self.messages: List[Message] = []
        self.max_history = max_history
        logger.info(f"Initialized conversation memory with max {max_history} messages")
    
    def add_message(self, role: str, content: str) -> None:
        """Add a message to memory.
        
        Args:
            role: Either 'user' or 'assistant'.
            content: The message content.
        """
        message = Message(role, content)
        self.messages.append(message)
        
        # Keep only recent messages
        if len(self.messages) > self.max_history:
            self.messages = self.messages[-self.max_history:]
        
        logger.debug(f"Added {role} message to memory")
    
    def get_conversation_context(self) -> str:
        """Get the conversation history as a formatted string.
        
        Returns:
            Formatted conversation history.
        """
        context = "Recent conversation history:\n"
        for msg in self.messages[-5:]:  # Last 5 messages
            context += f"{msg.role.upper()}: {msg.content}\n"
        return context
    
    def get_messages(self) -> List[Dict[str, Any]]:
        """Get all messages as dictionaries.
        
        Returns:
            List of message dictionaries.
        """
        return [msg.to_dict() for msg in self.messages]
    
    def clear(self) -> None:
        """Clear all messages."""
        self.messages = []
        logger.info("Cleared conversation memory")


class SessionManager:
    """Manages multiple conversation sessions."""
    
    def __init__(self):
        """Initialize session manager."""
        self.sessions: Dict[str, ConversationMemory] = {}
        logger.info("Initialized session manager")
    
    def get_or_create_session(self, session_id: str) -> ConversationMemory:
        """Get or create a session.
        
        Args:
            session_id: Unique identifier for the session.
            
        Returns:
            ConversationMemory instance for the session.
        """
        if session_id not in self.sessions:
            self.sessions[session_id] = ConversationMemory()
            logger.info(f"Created new session: {session_id}")
        return self.sessions[session_id]
    
    def delete_session(self, session_id: str) -> None:
        """Delete a session.
        
        Args:
            session_id: The session to delete.
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(f"Deleted session: {session_id}")


# Global session manager instance
_session_manager = None


def get_session_manager() -> SessionManager:
    """Get or create the session manager singleton."""
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionManager()
    return _session_manager
