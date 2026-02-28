import uuid
from typing import Dict, List, Optional, Any
from Source.ai.Multi_Agent_System.Memory.AdvancedMemoryManager import AdvancedMemoryManager


class SessionMemory:
    """
    Enhanced Session Memory với Advanced Memory Manager
    Kết hợp short-term (RAM) và long-term (persistent) memory
    """

    def __init__(self, use_advanced_memory: bool = True, storage_path: str = "memory_storage"):
        # Short-term memory (RAM) - cho session hiện tại
        self.sessions: Dict[str, List[Dict[str, Any]]] = {}
        
        # Advanced memory components
        self.use_advanced_memory = use_advanced_memory
        if use_advanced_memory:
            self.advanced_memory = AdvancedMemoryManager(storage_path)
        else:
            self.advanced_memory = None
        
        # User mapping (session_id -> user_id)
        self.session_to_user: Dict[str, str] = {}
        self.default_user_id = "default_user"

    def create_session(self, user_id: Optional[str] = None) -> str:
        """Tạo session mới"""
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = []
        
        if user_id:
            self.session_to_user[session_id] = user_id
        else:
            self.session_to_user[session_id] = self.default_user_id
        
        return session_id

    def get_history(self, session_id: str) -> List[Dict[str, Any]]:
        """Lấy history từ short-term memory"""
        return self.sessions.get(session_id, [])

    def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        save_to_long_term: bool = True
    ):
        """Thêm message vào session"""
        message = {
            "role": role,
            "content": content,
            "timestamp": str(uuid.uuid4())  # Simple timestamp
        }
        
        self.sessions.setdefault(session_id, []).append(message)
        
        # Save to advanced memory nếu được bật
        if self.use_advanced_memory and self.advanced_memory and save_to_long_term:
            user_id = self.session_to_user.get(session_id, self.default_user_id)
            # Lưu toàn bộ conversation khi có đủ messages
            # (có thể optimize bằng cách batch save)
            if len(self.sessions[session_id]) % 10 == 0:  # Save mỗi 10 messages
                self.advanced_memory.save_conversation(
                    session_id=session_id,
                    user_id=user_id,
                    messages=self.sessions[session_id]
                )
    
    def save_session_to_long_term(self, session_id: str):
        """Lưu session vào long-term memory"""
        if self.use_advanced_memory and self.advanced_memory:
            user_id = self.session_to_user.get(session_id, self.default_user_id)
            messages = self.sessions.get(session_id, [])
            
            if messages:
                self.advanced_memory.save_conversation(
                    session_id=session_id,
                    user_id=user_id,
                    messages=messages
                )
    
    def recall_semantic(
        self,
        query: str,
        session_id: Optional[str] = None,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """Semantic recall - tìm kiếm theo ngữ nghĩa"""
        if self.use_advanced_memory and self.advanced_memory:
            return self.advanced_memory.recall_semantic(query, top_k=top_k)
        return []
    
    def get_user_preference(
        self,
        session_id: str,
        key: str,
        default: Any = None
    ) -> Any:
        """Lấy user preference"""
        if self.use_advanced_memory and self.advanced_memory:
            user_id = self.session_to_user.get(session_id, self.default_user_id)
            return self.advanced_memory.get_preference(user_id, key, default)
        return default
    
    def save_user_preference(
        self,
        session_id: str,
        key: str,
        value: Any
    ):
        """Lưu user preference"""
        if self.use_advanced_memory and self.advanced_memory:
            user_id = self.session_to_user.get(session_id, self.default_user_id)
            self.advanced_memory.save_preference(user_id, key, value)
    
    def get_tool_recommendations(
        self,
        task_type: str,
        context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Đề xuất tools"""
        if self.use_advanced_memory and self.advanced_memory:
            return self.advanced_memory.get_tool_recommendations(task_type, context)
        return []
    
    def search_knowledge(
        self,
        query: str,
        categories: Optional[List[str]] = None,
        limit: int = 10
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Tìm kiếm trong knowledge base"""
        if self.use_advanced_memory and self.advanced_memory:
            return self.advanced_memory.search_knowledge(query, categories, limit)
        return {"facts": [], "relationships": [], "patterns": []}
    
    def get_memory_summary(self, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Lấy summary của memory"""
        if self.use_advanced_memory and self.advanced_memory:
            user_id = None
            if session_id:
                user_id = self.session_to_user.get(session_id)
            return self.advanced_memory.get_memory_summary(user_id)
        return {}