from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from Source.ai.Multi_Agent.Source.Main.Memory.memory.short_term_memory import ShortTermMemory
from Source.ai.Multi_Agent.Source.Main.Memory.memory.long_term_memory import long_term_memory

@dataclass
class Memory:
    def __init__(self):
        self.conversation_history = []
        self.user_preferences = {}
        self.session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    def add_message(self, role, content, save_to_long_term=True):
        #Thêm tin nhắn vào memory và optionally vào long-term storage
        timestamp = datetime.now().isoformat()
        message_entry = {
            "role": role,
            "content": content,
            "timestamp": timestamp
        }
        
        self.conversation_history.append(message_entry)
        
        # Lưu vào long-term memory
        if save_to_long_term:
            metadata = {
                "timestamp": timestamp,
                "session_id": self.session_id
            }
            long_term_memory.add_memory(self.session_id, role, content, metadata)
    
    def get_conversation_context(self, current_input):
        #Lấy ngữ cảnh từ cả short-term và long-term memory
        # Short-term context (recent messages)
        short_term_context = "\n".join(
            [f"{msg['role']}: {msg['content']}" 
             for msg in self.conversation_history[-5:]]  # Last 5 messages
        )
        
        # Long-term context (related memories)
        long_term_context = long_term_memory.get_conversation_context(
            current_input, self.session_id
        )
        
        return f"{long_term_context}\n\nLịch sử gần đây:\n{short_term_context}"
    
    def clear_memory(self):
        #Xóa cả short-term và long-term memory
        self.conversation_history = []
        self.user_preferences = {}
        self.session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        # long_term_memory.clear_memory()  # Uncomment if you want to clear long-term too

class MemoryManager:
    def __init__(self):
        self.active_sessions: Dict[str, ShortTermMemory] = {}
        self.memory = Memory()
    
    def _generate_session_id(self) -> str:
        return f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    def get_memory(self, user_id: str = "default_user") -> ShortTermMemory:
        """Lấy hoặc tạo memory cho user"""
        if user_id not in self.active_sessions:
            self.active_sessions[user_id] = ShortTermMemory(user_id)
        return self.active_sessions[user_id]

    def add_message(self, role: str, content: str, user_id: str = "default_user", save_to_long_term: bool = True) -> None: #
        """Thêm tin nhắn vào short-term và (tùy chọn) long-term."""
        stm = self.get_memory(user_id)
        stm.add_message(role=role, content=content, save_to_long_term=save_to_long_term)

    def update_preferences(self, key: str, value: Any, user_id: str = "default_user") -> None:
        stm = self.get_memory(user_id)
        stm.update_preferences(key, value)

    def update_booking(self, key: str, value: Any, user_id: str = "default_user") -> None:
        stm = self.get_memory(user_id)
        stm.update_booking(key, value)

    def get_recent_history(self, n: int = 5, user_id: str = "default_user") -> List[Dict[str, str]]:
        return self.get_memory(user_id).get_recent_history(n)

    def list_conversation_history(self, user_id: str = "default_user") -> List[Dict[str, str]]:
        return list(self.get_memory(user_id).conversation_history)

    def get_context_summary(self, user_id: str = "default_user", include_long_term: bool = False, current_input: Optional[str] = None) -> str:
        """Tạo summary context; có thể kèm long-term theo input hiện tại."""
        stm = self.get_memory(user_id)
        summary = stm.get_context_summary()
        if include_long_term and current_input:
            ltm_context = long_term_memory.get_conversation_context(current_input, session_id=stm.session_id)
            return f"{summary}\n\n{ltm_context}"
        return summary

    def get_session_id(self, user_id: str = "default_user") -> str:
        return self.get_memory(user_id).session_id

    def start_new_session(
        self,
        user_id: str = "default_user",
        clear_history: bool = True,
        keep_preferences: bool = True,
    ) -> str:
        stm = self.get_memory(user_id)
        if clear_history:
            stm.conversation_history = []
            stm.booking_info = {}
        if not keep_preferences:
            stm.user_preferences = {}
        stm.session_id = self._generate_session_id()
        stm.last_updated = datetime.now()
        return stm.session_id

    def clear_memory(self, user_id: str = "default_user", also_long_term: bool = False) -> None:
        stm = self.get_memory(user_id)
        stm.clear_memory()
        if also_long_term:
            # Xóa toàn bộ long-term store (cả collection). Cân nhắc nếu muốn chỉ xóa theo session.
            long_term_memory.clear_memory()

    def list_sessions(self) -> List[str]:
        """Liệt kê tất cả session_id đang có trong long-term memory."""
        results = long_term_memory.collection.get(include=["metadatas"]) or {}
        metadatas = results.get("metadatas") or []
        session_ids = sorted({m.get("session_id") for m in metadatas if m and m.get("session_id")})
        return session_ids

    def resume_session(self, session_id: str, user_id: str = "default_user", replay_last_n: Optional[int] = 20) -> int:
        stm = self.get_memory(user_id)
        stm.session_id = session_id

        results = long_term_memory.collection.get(
            where={"session_id": session_id}, include=["documents", "metadatas"]
        ) or {}

        documents = results.get("documents") or []
        metadatas = results.get("metadatas") or []

        records: List[tuple] = []
        for doc, meta in zip(documents, metadatas):
            timestamp = (meta or {}).get("timestamp", "")
            role = (meta or {}).get("role", "system")
            content = doc
            if isinstance(doc, str) and ": " in doc:
                content = doc.split(": ", 1)[1]
            records.append((timestamp, role, content))

        records.sort(key=lambda x: x[0])
        if replay_last_n is not None:
            records = records[-replay_last_n:]

        for _, role, content in records:
            stm.add_message(role, content, save_to_long_term=False)

        return len(records)
    
    def cleanup_old_sessions(self, hours: int = 1):
        """Dọn dẹp session cũ"""
        now = datetime.now()
        to_remove = []
        
        for user_id, memory in self.active_sessions.items():
            if (now - memory.last_updated).total_seconds() > hours * 3600:
                to_remove.append(user_id)
        
        for user_id in to_remove:
            del self.active_sessions[user_id]

# Shared singleton for all agents to use
memory_manager = MemoryManager()