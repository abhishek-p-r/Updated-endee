"""
AI Agent Memory System - Persistent Storage & Context Management
Stores conversations, documents, insights, and user preferences
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path
import uuid

# Memory storage directory
MEMORY_DIR = Path("memory_store")
MEMORY_DIR.mkdir(exist_ok=True)

CONVERSATIONS_FILE = MEMORY_DIR / "conversations.json"
DOCUMENTS_FILE = MEMORY_DIR / "documents.json"
INSIGHTS_FILE = MEMORY_DIR / "insights.json"
PREFERENCES_FILE = MEMORY_DIR / "preferences.json"
CONTEXT_FILE = MEMORY_DIR / "context.json"


class AgentMemory:
    """AI Agent Memory System for persistent storage and context"""
    
    def __init__(self):
        self.ensure_files_exist()
    
    def ensure_files_exist(self):
        """Ensure all memory files exist"""
        for file_path in [CONVERSATIONS_FILE, DOCUMENTS_FILE, INSIGHTS_FILE, 
                         PREFERENCES_FILE, CONTEXT_FILE]:
            if not file_path.exists():
                file_path.write_text(json.dumps([]))
    
    # ========== CONVERSATION MEMORY ==========
    
    def add_conversation(self, user_query: str, ai_response: str, 
                        metadata: Dict = None) -> str:
        """Store conversation message"""
        conversations = self._read_json(CONVERSATIONS_FILE)
        
        conv_id = str(uuid.uuid4())
        conversation = {
            "id": conv_id,
            "user_query": user_query,
            "ai_response": ai_response,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        conversations.append(conversation)
        self._write_json(CONVERSATIONS_FILE, conversations)
        
        # Update context
        self._update_context(user_query, ai_response)
        
        return conv_id
    
    def get_conversation_history(self, limit: int = 20) -> List[Dict]:
        """Get recent conversation history"""
        conversations = self._read_json(CONVERSATIONS_FILE)
        return conversations[-limit:]
    
    def get_all_conversations(self) -> List[Dict]:
        """Get all conversations"""
        return self._read_json(CONVERSATIONS_FILE)
    
    def search_conversations(self, keyword: str) -> List[Dict]:
        """Search conversations by keyword"""
        conversations = self._read_json(CONVERSATIONS_FILE)
        return [
            c for c in conversations 
            if keyword.lower() in c["user_query"].lower() or 
               keyword.lower() in c["ai_response"].lower()
        ]
    
    # ========== DOCUMENT MEMORY ==========
    
    def add_document(self, filename: str, content: str, 
                    doc_type: str = "text") -> str:
        """Store uploaded document"""
        documents = self._read_json(DOCUMENTS_FILE)
        
        doc_id = str(uuid.uuid4())
        document = {
            "id": doc_id,
            "filename": filename,
            "content": content[:5000],  # Store preview
            "full_content": content,  # Full content for Q&A
            "type": doc_type,
            "size": len(content),
            "uploaded_at": datetime.now().isoformat()
        }
        
        documents.append(document)
        self._write_json(DOCUMENTS_FILE, documents)
        
        return doc_id
    
    def get_documents(self) -> List[Dict]:
        """Get all stored documents"""
        docs = self._read_json(DOCUMENTS_FILE)
        # Return without full_content for efficiency
        return [
            {k: v for k, v in doc.items() if k != "full_content"}
            for doc in docs
        ]
    
    def get_document_content(self, doc_id: str) -> Optional[str]:
        """Get full document content"""
        documents = self._read_json(DOCUMENTS_FILE)
        for doc in documents:
            if doc["id"] == doc_id:
                return doc.get("full_content", doc.get("content"))
        return None
    
    def remove_document(self, doc_id: str) -> bool:
        """Delete stored document"""
        documents = self._read_json(DOCUMENTS_FILE)
        documents = [d for d in documents if d["id"] != doc_id]
        self._write_json(DOCUMENTS_FILE, documents)
        return True
    
    # ========== INSIGHTS MEMORY ==========
    
    def add_insight(self, topic: str, insight: str, depth: str = "medium") -> str:
        """Store generated insight"""
        insights = self._read_json(INSIGHTS_FILE)
        
        insight_id = str(uuid.uuid4())
        insight_obj = {
            "id": insight_id,
            "topic": topic,
            "content": insight,
            "depth": depth,
            "created_at": datetime.now().isoformat()
        }
        
        insights.append(insight_obj)
        self._write_json(INSIGHTS_FILE, insights)
        
        return insight_id
    
    def get_insights(self) -> List[Dict]:
        """Get all stored insights"""
        return self._read_json(INSIGHTS_FILE)
    
    def get_insight(self, insight_id: str) -> Optional[Dict]:
        """Get specific insight"""
        insights = self._read_json(INSIGHTS_FILE)
        for insight in insights:
            if insight["id"] == insight_id:
                return insight
        return None
    
    # ========== PREFERENCES ==========
    
    def set_preference(self, key: str, value: Any):
        """Store user preference"""
        preferences = self._read_json(PREFERENCES_FILE)
        
        # Convert list to dict if needed
        if isinstance(preferences, list):
            preferences = {}
        
        preferences[key] = value
        self._write_json(PREFERENCES_FILE, preferences)
    
    def get_preference(self, key: str, default: Any = None) -> Any:
        """Get user preference"""
        preferences = self._read_json(PREFERENCES_FILE)
        
        if isinstance(preferences, list):
            return default
        
        return preferences.get(key, default)
    
    def get_all_preferences(self) -> Dict:
        """Get all preferences"""
        prefs = self._read_json(PREFERENCES_FILE)
        return prefs if isinstance(prefs, dict) else {}
    
    # ========== CONTEXT AWARENESS ==========
    
    def _update_context(self, user_query: str, ai_response: str):
        """Update context for awareness"""
        context = self._read_json(CONTEXT_FILE)
        
        if not isinstance(context, dict):
            context = {
                "last_topic": None,
                "mentioned_topics": [],
                "user_style": [],
                "last_query": None,
                "queries_in_session": 0
            }
        
        # Extract key topics
        topics = self._extract_topics(user_query)
        
        context["last_topic"] = topics[0] if topics else None
        context["mentioned_topics"] = list(set(
            context.get("mentioned_topics", []) + topics
        ))[-10:]  # Keep last 10
        context["last_query"] = user_query
        context["queries_in_session"] = context.get("queries_in_session", 0) + 1
        
        self._write_json(CONTEXT_FILE, context)
    
    def get_context(self) -> Dict:
        """Get current context"""
        context = self._read_json(CONTEXT_FILE)
        if not isinstance(context, dict):
            return {
                "last_topic": None,
                "mentioned_topics": [],
                "queries_in_session": 0,
                "last_query": None
            }
        return context
    
    def get_memory_summary(self) -> Dict:
        """Get summary of all stored memory"""
        return {
            "total_conversations": len(self._read_json(CONVERSATIONS_FILE)),
            "documents_stored": len(self._read_json(DOCUMENTS_FILE)),
            "insights_saved": len(self._read_json(INSIGHTS_FILE)),
            "preferences": len(self.get_all_preferences()),
            "context": self.get_context()
        }
    
    def clear_all_memory(self):
        """Clear all stored memory (caution!)"""
        self._write_json(CONVERSATIONS_FILE, [])
        self._write_json(DOCUMENTS_FILE, [])
        self._write_json(INSIGHTS_FILE, [])
        self._write_json(PREFERENCES_FILE, {})
        self._write_json(CONTEXT_FILE, {})
    
    def clear_conversations(self):
        """Clear only conversations"""
        self._write_json(CONVERSATIONS_FILE, [])
    
    def export_memory(self) -> Dict:
        """Export all memory as JSON"""
        return {
            "conversations": self.get_all_conversations(),
            "documents": self.get_documents(),
            "insights": self.get_insights(),
            "preferences": self.get_all_preferences(),
            "summary": self.get_memory_summary(),
            "exported_at": datetime.now().isoformat()
        }
    
    # ========== UTILITY METHODS ==========
    
    def _read_json(self, filepath: Path) -> Any:
        """Read JSON file safely"""
        try:
            if filepath.exists():
                return json.loads(filepath.read_text())
            return []
        except:
            return []
    
    def _write_json(self, filepath: Path, data: Any):
        """Write JSON file safely"""
        try:
            filepath.write_text(json.dumps(data, indent=2))
        except Exception as e:
            print(f"Error writing to {filepath}: {e}")
    
    def _extract_topics(self, text: str) -> List[str]:
        """Extract key topics from text"""
        # Simple keyword extraction
        keywords = ["python", "javascript", "ai", "machine learning", 
                   "web", "api", "database", "backend", "frontend",
                   "security", "performance", "design", "ux", "ui"]
        topics = []
        text_lower = text.lower()
        for keyword in keywords:
            if keyword in text_lower:
                topics.append(keyword)
        return topics


# Global memory instance
memory_manager = AgentMemory()


def get_memory_manager() -> AgentMemory:
    """Get global memory manager instance"""
    return memory_manager
