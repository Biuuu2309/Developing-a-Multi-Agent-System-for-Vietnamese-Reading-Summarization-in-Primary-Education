from typing import Dict, List, Any, Optional
from datetime import datetime
import sys
from pathlib import Path

# Handle both relative and absolute imports
try:
    from .LongTermMemory import LongTermMemory
    from .SemanticMemory import SemanticMemory
    from .ToolMemory import ToolMemory
    from .KnowledgeBase import KnowledgeBase
except ImportError:
    # Fallback for direct import
    sys.path.insert(0, str(Path(__file__).parent))
    from LongTermMemory import LongTermMemory
    from SemanticMemory import SemanticMemory
    from ToolMemory import ToolMemory
    from KnowledgeBase import KnowledgeBase


class AdvancedMemoryManager:
    """
    Advanced Memory Manager
    Tích hợp tất cả memory components:
    - Long-term memory (persistent)
    - Semantic memory (embedding-based)
    - Tool memory (tool usage tracking)
    - Knowledge base (knowledge accumulation)
    """
    
    def __init__(self, storage_path: str = "memory_storage"):
        self.storage_path = storage_path
        
        # Initialize all memory components
        self.long_term = LongTermMemory(storage_path)
        self.semantic = SemanticMemory(storage_path)
        self.tool_memory = ToolMemory(storage_path)
        self.knowledge_base = KnowledgeBase(storage_path)
    
    def save_conversation(
        self,
        session_id: str,
        user_id: str,
        messages: List[Dict[str, Any]],
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Lưu conversation vào long-term và semantic memory"""
        # Save to long-term
        self.long_term.save_conversation(session_id, user_id, messages, metadata)
        
        # Store important messages in semantic memory
        for msg in messages:
            content = msg.get("content", "")
            role = msg.get("role", "")
            
            # Store user messages và important assistant responses
            if role == "user" and len(content) > 50:
                self.semantic.store(
                    content=content,
                    content_type="user_message",
                    metadata={"session_id": session_id, "user_id": user_id, "role": role}
                )
            elif role == "assistant" and len(content) > 100:
                # Store longer assistant responses
                self.semantic.store(
                    content=content,
                    content_type="assistant_response",
                    metadata={"session_id": session_id, "user_id": user_id, "role": role}
                )
        
        # Extract knowledge từ conversation
        self.knowledge_base.extract_knowledge_from_conversation(messages, user_id)
    
    def recall_semantic(
        self,
        query: str,
        content_type: Optional[str] = None,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """Semantic recall - tìm kiếm theo ngữ nghĩa"""
        return self.semantic.search(query, content_type, top_k)
    
    def recall_conversation(
        self,
        user_id: str,
        query: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Recall conversations"""
        if query:
            # Semantic search
            results = self.semantic.search(query, "user_message", top_k=limit or 10)
            return [r.get("metadata", {}) for r in results]
        else:
            # Get recent conversations
            return self.long_term.get_user_conversations(user_id, limit)
    
    def record_tool_usage(
        self,
        tool_name: str,
        input_data: Dict[str, Any],
        output: Any,
        success: bool,
        execution_time: Optional[float] = None,
        agent_name: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        """Ghi lại tool usage"""
        self.tool_memory.record_tool_usage(
            tool_name, input_data, output, success,
            execution_time, agent_name, context
        )
    
    def get_tool_recommendations(
        self,
        task_type: str,
        context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Đề xuất tools"""
        return self.tool_memory.get_recommended_tools(task_type, context)
    
    def save_preference(
        self,
        user_id: str,
        key: str,
        value: Any
    ):
        """Lưu user preference"""
        self.long_term.save_preference(user_id, key, value)
    
    def get_preference(
        self,
        user_id: str,
        key: str,
        default: Any = None
    ) -> Any:
        """Lấy user preference"""
        return self.long_term.get_preference(user_id, key, default)
    
    def save_fact(
        self,
        user_id: str,
        fact: str,
        source: Optional[str] = None,
        importance: float = 0.5
    ):
        """Lưu important fact"""
        self.long_term.save_fact(user_id, fact, source, importance)
        # Cũng lưu vào knowledge base
        self.knowledge_base.add_fact(
            category="user_facts",
            fact=fact,
            source=source,
            confidence=importance
        )
    
    def get_facts(
        self,
        user_id: str,
        min_importance: float = 0.0,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Lấy facts"""
        return self.long_term.get_facts(user_id, min_importance, limit)
    
    def search_knowledge(
        self,
        query: str,
        categories: Optional[List[str]] = None,
        limit: int = 10
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Tìm kiếm trong knowledge base"""
        return self.knowledge_base.search_knowledge(query, categories, limit)
    
    def get_memory_summary(
        self,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Lấy summary của tất cả memory"""
        summary = {
            "long_term": self.long_term.get_memory_summary(user_id) if user_id else {},
            "semantic": self.semantic.get_stats(),
            "tool_memory": self.tool_memory.get_tool_usage_summary(),
            "knowledge_base": self.knowledge_base.get_knowledge_summary()
        }
        
        return summary
