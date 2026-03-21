from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import os
from pathlib import Path


class LongTermMemory:
    """
    Long-term Memory với persistent storage
    Lưu trữ:
    - Conversation history (persistent)
    - User preferences
    - Important facts
    - Patterns và insights
    """
    
    def __init__(self, storage_path: str = "memory_storage"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        
        # File paths
        self.conversations_file = self.storage_path / "conversations.json"
        self.preferences_file = self.storage_path / "preferences.json"
        self.facts_file = self.storage_path / "facts.json"
        self.patterns_file = self.storage_path / "patterns.json"
        
        # Load existing data
        self.conversations = self._load_json(self.conversations_file, {})
        self.preferences = self._load_json(self.preferences_file, {})
        self.facts = self._load_json(self.facts_file, {})
        self.patterns = self._load_json(self.patterns_file, {})
    
    def _load_json(self, file_path: Path, default: Any) -> Any:
        """Load JSON file"""
        if file_path.exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return default
        return default
    
    def _save_json(self, file_path: Path, data: Any):
        """Save JSON file"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except IOError as e:
            print(f"Error saving to {file_path}: {e}")
    
    def save_conversation(
        self,
        session_id: str,
        user_id: str,
        messages: List[Dict[str, Any]],
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Lưu conversation vào long-term memory"""
        if user_id not in self.conversations:
            self.conversations[user_id] = []
        
        conversation_entry = {
            "session_id": session_id,
            "timestamp": datetime.now().isoformat(),
            "messages": messages,
            "message_count": len(messages),
            "metadata": metadata or {}
        }
        
        self.conversations[user_id].append(conversation_entry)
        
        # Giới hạn số lượng conversations per user (giữ 100 gần nhất)
        if len(self.conversations[user_id]) > 100:
            self.conversations[user_id] = self.conversations[user_id][-100:]
        
        self._save_json(self.conversations_file, self.conversations)
    
    def get_user_conversations(
        self,
        user_id: str,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Lấy conversations của user"""
        conversations = self.conversations.get(user_id, [])
        if limit:
            return conversations[-limit:]
        return conversations
    
    def save_preference(
        self,
        user_id: str,
        key: str,
        value: Any
    ):
        """Lưu user preference"""
        if user_id not in self.preferences:
            self.preferences[user_id] = {}
        
        self.preferences[user_id][key] = {
            "value": value,
            "updated_at": datetime.now().isoformat()
        }
        
        self._save_json(self.preferences_file, self.preferences)
    
    def get_preference(
        self,
        user_id: str,
        key: str,
        default: Any = None
    ) -> Any:
        """Lấy user preference"""
        user_prefs = self.preferences.get(user_id, {})
        pref = user_prefs.get(key, {})
        return pref.get("value", default) if isinstance(pref, dict) else default
    
    def get_all_preferences(self, user_id: str) -> Dict[str, Any]:
        """Lấy tất cả preferences của user"""
        user_prefs = self.preferences.get(user_id, {})
        return {
            key: pref.get("value") if isinstance(pref, dict) else pref
            for key, pref in user_prefs.items()
        }
    
    def save_fact(
        self,
        user_id: str,
        fact: str,
        source: Optional[str] = None,
        importance: float = 0.5
    ):
        """Lưu important fact"""
        if user_id not in self.facts:
            self.facts[user_id] = []
        
        fact_entry = {
            "fact": fact,
            "source": source,
            "importance": importance,
            "timestamp": datetime.now().isoformat()
        }
        
        self.facts[user_id].append(fact_entry)
        
        # Sắp xếp theo importance
        self.facts[user_id].sort(key=lambda x: x["importance"], reverse=True)
        
        # Giới hạn số lượng facts (giữ 200 quan trọng nhất)
        if len(self.facts[user_id]) > 200:
            self.facts[user_id] = self.facts[user_id][:200]
        
        self._save_json(self.facts_file, self.facts)
    
    def get_facts(
        self,
        user_id: str,
        min_importance: float = 0.0,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Lấy facts của user"""
        user_facts = self.facts.get(user_id, [])
        filtered = [f for f in user_facts if f["importance"] >= min_importance]
        
        if limit:
            return filtered[:limit]
        return filtered
    
    def save_pattern(
        self,
        pattern_type: str,
        pattern: Dict[str, Any],
        user_id: Optional[str] = None
    ):
        """Lưu pattern hoặc insight"""
        key = f"{user_id}_{pattern_type}" if user_id else pattern_type
        
        if key not in self.patterns:
            self.patterns[key] = []
        
        pattern_entry = {
            "pattern": pattern,
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id
        }
        
        self.patterns[key].append(pattern_entry)
        
        # Giới hạn số lượng patterns
        if len(self.patterns[key]) > 50:
            self.patterns[key] = self.patterns[key][-50:]
        
        self._save_json(self.patterns_file, self.patterns)
    
    def get_patterns(
        self,
        pattern_type: str,
        user_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Lấy patterns"""
        key = f"{user_id}_{pattern_type}" if user_id else pattern_type
        return self.patterns.get(key, [])
    
    def search_conversations(
        self,
        user_id: str,
        query: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Tìm kiếm conversations (simple text search)"""
        conversations = self.get_user_conversations(user_id)
        results = []
        
        query_lower = query.lower()
        
        for conv in conversations:
            # Tìm trong messages
            for msg in conv.get("messages", []):
                content = msg.get("content", "").lower()
                if query_lower in content:
                    results.append({
                        "conversation": conv,
                        "matched_message": msg,
                        "relevance": 1.0  # Simple match
                    })
                    break
        
        return results[:limit]
    
    def get_memory_summary(self, user_id: str) -> Dict[str, Any]:
        """Lấy summary của memory"""
        return {
            "conversations_count": len(self.conversations.get(user_id, [])),
            "preferences_count": len(self.preferences.get(user_id, {})),
            "facts_count": len(self.facts.get(user_id, [])),
            "patterns_count": sum(
                len(patterns) for key, patterns in self.patterns.items()
                if not user_id or key.startswith(f"{user_id}_")
            )
        }
