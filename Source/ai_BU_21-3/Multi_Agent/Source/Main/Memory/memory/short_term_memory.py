from typing import List, Dict, Any
from dataclasses import dataclass
from datetime import datetime
import json
from Source.ai.Multi_Agent.Source.Main.Memory.memory.long_term_memory import long_term_memory

# Short-Term Memory System
@dataclass
class ShortTermMemory:
    user_id: str
    conversation_history: List[Dict[str, str]]
    user_preferences: Dict[str, Any]
    booking_info: Dict[str, Any]
    last_updated: datetime
    session_id: str
    
    def __init__(self, user_id: str = "default_user"):
        self.user_id = user_id
        self.conversation_history = []
        self.user_preferences = {}
        self.booking_info = {}
        self.last_updated = datetime.now()
        self.session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    def add_message(self, role: str, content: str, save_to_long_term: bool = True):
        """Thêm message vào lịch sử hội thoại và (tùy chọn) lưu long-term."""
        timestamp = datetime.now().isoformat()
        self.conversation_history.append({
            "role": role,
            "content": content,
            "timestamp": timestamp
        })
        self.last_updated = datetime.now()

        if save_to_long_term:
            metadata = {"timestamp": timestamp, "user_id": self.user_id}
            long_term_memory.add_memory(
                session_id=self.session_id,
                role=role,
                content=content,
                metadata=metadata,
            )
    
    def update_preferences(self, key: str, value: Any):
        """Cập nhật preference của user"""
        self.user_preferences[key] = value
        self.last_updated = datetime.now()
    
    def update_booking(self, key: str, value: Any):
        """Cập nhật thông tin booking"""
        self.booking_info[key] = value
        self.last_updated = datetime.now()
    
    def get_recent_history(self, n: int = 5) -> List[Dict[str, str]]:
        """Lấy n message gần nhất"""
        return self.conversation_history[-n:]
    
    def get_context_summary(self) -> str:
        """Tạo summary context từ memory"""
        summary = f"Session: {self.session_id}\n"
        
        if self.user_preferences:
            summary += f"Preferences: {json.dumps(self.user_preferences, ensure_ascii=False)}\n"
        
        if self.booking_info:
            summary += f"Booking Info: {json.dumps(self.booking_info, ensure_ascii=False)}\n"
        
        # Thêm 3 message gần nhất
        recent_msgs = self.get_recent_history(3)
        if recent_msgs:
            summary += "Recent conversation:\n"
            for msg in recent_msgs:
                summary += f"{msg['role']}: {msg['content']}\n"
        
        return summary
    
    def clear_memory(self):
        """Xóa memory (giữ lại preferences)"""
        self.conversation_history = []
        self.booking_info = {}
        self.last_updated = datetime.now()
        
short_term_memory = ShortTermMemory()