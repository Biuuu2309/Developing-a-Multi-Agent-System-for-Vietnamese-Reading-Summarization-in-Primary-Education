from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path
import json
from collections import defaultdict


class KnowledgeBase:
    """
    Knowledge Accumulation
    Tích lũy kiến thức từ conversations và experiences:
    - Facts và information
    - Relationships
    - Patterns
    - Domain knowledge
    """
    
    def __init__(self, storage_path: str = "memory_storage"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        
        self.knowledge_file = self.storage_path / "knowledge_base.json"
        
        # Knowledge storage
        self.facts: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.relationships: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.patterns: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.domain_knowledge: Dict[str, Any] = {}
        
        # Load existing data
        self._load_data()
    
    def _load_data(self):
        """Load knowledge base"""
        if self.knowledge_file.exists():
            try:
                with open(self.knowledge_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.facts = defaultdict(list, data.get("facts", {}))
                    self.relationships = defaultdict(list, data.get("relationships", {}))
                    self.patterns = defaultdict(list, data.get("patterns", {}))
                    self.domain_knowledge = data.get("domain_knowledge", {})
            except (json.JSONDecodeError, IOError):
                pass
    
    def _save_data(self):
        """Save knowledge base"""
        try:
            data = {
                "facts": dict(self.facts),
                "relationships": dict(self.relationships),
                "patterns": dict(self.patterns),
                "domain_knowledge": self.domain_knowledge,
                "updated_at": datetime.now().isoformat()
            }
            with open(self.knowledge_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except IOError as e:
            print(f"Error saving knowledge base: {e}")
    
    def add_fact(
        self,
        category: str,
        fact: str,
        source: Optional[str] = None,
        confidence: float = 0.5,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Thêm fact vào knowledge base"""
        fact_entry = {
            "fact": fact,
            "source": source,
            "confidence": confidence,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        self.facts[category].append(fact_entry)
        
        # Giới hạn số lượng facts per category
        if len(self.facts[category]) > 500:
            # Giữ những facts có confidence cao nhất
            self.facts[category].sort(key=lambda x: x["confidence"], reverse=True)
            self.facts[category] = self.facts[category][:500]
        
        self._save_data()
    
    def get_facts(
        self,
        category: Optional[str] = None,
        min_confidence: float = 0.0,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Lấy facts"""
        if category:
            facts = self.facts.get(category, [])
        else:
            # Lấy từ tất cả categories
            facts = []
            for cat_facts in self.facts.values():
                facts.extend(cat_facts)
        
        # Filter by confidence
        filtered = [f for f in facts if f["confidence"] >= min_confidence]
        
        # Sort by confidence
        filtered.sort(key=lambda x: x["confidence"], reverse=True)
        
        if limit:
            return filtered[:limit]
        
        return filtered
    
    def add_relationship(
        self,
        entity1: str,
        relationship_type: str,
        entity2: str,
        strength: float = 0.5,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Thêm relationship"""
        rel_key = f"{entity1}_{relationship_type}"
        
        rel_entry = {
            "entity1": entity1,
            "relationship_type": relationship_type,
            "entity2": entity2,
            "strength": strength,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        self.relationships[rel_key].append(rel_entry)
        
        # Giới hạn số lượng relationships
        if len(self.relationships[rel_key]) > 100:
            self.relationships[rel_key] = self.relationships[rel_key][-100:]
        
        self._save_data()
    
    def get_relationships(
        self,
        entity: str,
        relationship_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Lấy relationships của entity"""
        results = []
        
        for rel_key, rels in self.relationships.items():
            for rel in rels:
                if rel["entity1"] == entity or rel["entity2"] == entity:
                    if relationship_type is None or rel["relationship_type"] == relationship_type:
                        results.append(rel)
        
        return results
    
    def add_pattern(
        self,
        pattern_type: str,
        pattern: Dict[str, Any],
        frequency: int = 1,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Thêm pattern"""
        pattern_entry = {
            "pattern": pattern,
            "frequency": frequency,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        # Check nếu pattern đã tồn tại
        existing = None
        for existing_pattern in self.patterns[pattern_type]:
            if existing_pattern["pattern"] == pattern:
                existing = existing_pattern
                break
        
        if existing:
            # Update frequency
            existing["frequency"] += frequency
            existing["timestamp"] = datetime.now().isoformat()
        else:
            # Add new pattern
            self.patterns[pattern_type].append(pattern_entry)
        
        # Sort by frequency
        self.patterns[pattern_type].sort(key=lambda x: x["frequency"], reverse=True)
        
        # Giới hạn số lượng patterns
        if len(self.patterns[pattern_type]) > 200:
            self.patterns[pattern_type] = self.patterns[pattern_type][:200]
        
        self._save_data()
    
    def get_patterns(
        self,
        pattern_type: str,
        min_frequency: int = 1,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Lấy patterns"""
        patterns = self.patterns.get(pattern_type, [])
        filtered = [p for p in patterns if p["frequency"] >= min_frequency]
        
        if limit:
            return filtered[:limit]
        
        return filtered
    
    def update_domain_knowledge(
        self,
        domain: str,
        knowledge: Dict[str, Any]
    ):
        """Cập nhật domain knowledge"""
        if domain not in self.domain_knowledge:
            self.domain_knowledge[domain] = {
                "knowledge": {},
                "updated_at": datetime.now().isoformat()
            }
        
        # Merge knowledge
        self.domain_knowledge[domain]["knowledge"].update(knowledge)
        self.domain_knowledge[domain]["updated_at"] = datetime.now().isoformat()
        
        self._save_data()
    
    def get_domain_knowledge(
        self,
        domain: str
    ) -> Optional[Dict[str, Any]]:
        """Lấy domain knowledge"""
        domain_data = self.domain_knowledge.get(domain)
        if domain_data:
            return domain_data.get("knowledge", {})
        return None
    
    def extract_knowledge_from_conversation(
        self,
        conversation: List[Dict[str, Any]],
        user_id: Optional[str] = None
    ):
        """Extract knowledge từ conversation"""
        # Simple extraction: tìm facts và patterns
        for msg in conversation:
            content = msg.get("content", "")
            role = msg.get("role", "")
            
            # Extract facts từ user messages (có thể cải thiện với NLP)
            if role == "user" and len(content) > 50:
                # Simple heuristic: nếu có "là", "có", "của" thì có thể là fact
                if any(keyword in content.lower() for keyword in ["là", "có", "của", "về"]):
                    self.add_fact(
                        category="user_info",
                        fact=content[:200],  # Limit length
                        source=f"conversation_{user_id}",
                        confidence=0.3
                    )
            
            # Extract patterns từ assistant responses
            if role == "assistant":
                # Có thể extract patterns về successful strategies
                if "tóm tắt" in content.lower() or "summary" in content.lower():
                    self.add_pattern(
                        pattern_type="summarization_response",
                        pattern={"content_length": len(content)},
                        frequency=1
                    )
    
    def search_knowledge(
        self,
        query: str,
        categories: Optional[List[str]] = None,
        limit: int = 10
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Tìm kiếm trong knowledge base"""
        results = {
            "facts": [],
            "relationships": [],
            "patterns": []
        }
        
        query_lower = query.lower()
        
        # Search facts
        fact_categories = categories if categories else self.facts.keys()
        for category in fact_categories:
            for fact in self.facts.get(category, []):
                if query_lower in fact["fact"].lower():
                    results["facts"].append(fact)
        
        # Search relationships
        for rels in self.relationships.values():
            for rel in rels:
                if (query_lower in rel["entity1"].lower() or 
                    query_lower in rel["entity2"].lower() or
                    query_lower in rel["relationship_type"].lower()):
                    results["relationships"].append(rel)
        
        # Search patterns
        for patterns in self.patterns.values():
            for pattern in patterns:
                pattern_str = str(pattern["pattern"]).lower()
                if query_lower in pattern_str:
                    results["patterns"].append(pattern)
        
        # Limit results
        for key in results:
            results[key] = results[key][:limit]
        
        return results
    
    def get_knowledge_summary(self) -> Dict[str, Any]:
        """Lấy summary của knowledge base"""
        return {
            "total_facts": sum(len(facts) for facts in self.facts.values()),
            "fact_categories": list(self.facts.keys()),
            "total_relationships": sum(len(rels) for rels in self.relationships.values()),
            "total_patterns": sum(len(patterns) for patterns in self.patterns.values()),
            "pattern_types": list(self.patterns.keys()),
            "domains": list(self.domain_knowledge.keys())
        }
