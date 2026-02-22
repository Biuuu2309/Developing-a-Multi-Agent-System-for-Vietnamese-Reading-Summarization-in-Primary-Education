# memory.py

from typing import Dict, List, Any, Optional
from datetime import datetime
from collections import deque


# ==============================
# Short-Term Conversation Memory
# ==============================

class ConversationMemory:
    """
    Short-term memory for a single session.
    Keeps recent conversation context for Coordinator.
    """

    def __init__(self, user_id: str, max_messages: int = 10):
        self.user_id = user_id
        self.session_id = self._generate_session_id()
        self.max_messages = max_messages
        self.conversation_history = deque(maxlen=max_messages)
        self.user_preferences: Dict[str, Any] = {}
        self.last_updated = datetime.now()

    def _generate_session_id(self) -> str:
        return f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    def add_message(self, role: str, content: str) -> None:
        self.conversation_history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        self.last_updated = datetime.now()

    def get_recent_history(self, n: int = 5) -> List[Dict[str, str]]:
        return list(self.conversation_history)[-n:]

    def get_context_string(self, n: int = 5) -> str:
        messages = self.get_recent_history(n)
        return "\n".join([f"{m['role']}: {m['content']}" for m in messages])

    def clear(self, keep_preferences: bool = True) -> None:
        self.conversation_history.clear()
        if not keep_preferences:
            self.user_preferences = {}
        self.session_id = self._generate_session_id()
        self.last_updated = datetime.now()


# ==============================
# Memory Manager
# ==============================

class MemoryManager:
    """
    Central memory manager for MAS.
    Handles conversation memory only.
    Experience memory is separated.
    """

    def __init__(self):
        self.active_sessions: Dict[str, ConversationMemory] = {}

    def get_memory(self, user_id: str = "default_user") -> ConversationMemory:
        if user_id not in self.active_sessions:
            self.active_sessions[user_id] = ConversationMemory(user_id)
        return self.active_sessions[user_id]

    def add_message(self, role: str, content: str, user_id: str = "default_user") -> None:
        memory = self.get_memory(user_id)
        memory.add_message(role, content)

    def get_context(self, user_id: str = "default_user", n: int = 5) -> str:
        return self.get_memory(user_id).get_context_string(n)

    def start_new_session(
        self,
        user_id: str = "default_user",
        keep_preferences: bool = True
    ) -> str:
        memory = self.get_memory(user_id)
        memory.clear(keep_preferences=keep_preferences)
        return memory.session_id

    def cleanup_old_sessions(self, hours: int = 1) -> None:
        now = datetime.now()
        to_remove = []

        for user_id, memory in self.active_sessions.items():
            delta = (now - memory.last_updated).total_seconds()
            if delta > hours * 3600:
                to_remove.append(user_id)

        for user_id in to_remove:
            del self.active_sessions[user_id]


# Shared singleton
memory_manager = MemoryManager()