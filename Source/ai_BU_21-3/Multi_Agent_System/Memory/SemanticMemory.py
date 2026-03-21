from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import numpy as np
from pathlib import Path
import json
import pickle


class SemanticMemory:
    """
    Semantic Memory với embedding-based search
    Sử dụng vector embeddings để tìm kiếm theo ngữ nghĩa
    """
    
    def __init__(
        self,
        storage_path: str = "memory_storage",
        embedding_dim: int = 384  # Có thể dùng sentence-transformers
    ):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        # Đảm bảo embedding_dim là int
        self.embedding_dim = int(embedding_dim) if embedding_dim is not None else 384
        
        # File paths
        self.embeddings_file = self.storage_path / "semantic_embeddings.pkl"
        self.metadata_file = self.storage_path / "semantic_metadata.json"
        
        # In-memory storage
        self.embeddings: Dict[str, np.ndarray] = {}
        self.metadata: Dict[str, Dict[str, Any]] = {}
        
        # Load existing data
        self._load_data()
    
    def _load_data(self):
        """Load embeddings và metadata"""
        # Load metadata
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    self.metadata = json.load(f)
            except (json.JSONDecodeError, IOError):
                self.metadata = {}
        
        # Load embeddings
        if self.embeddings_file.exists():
            try:
                with open(self.embeddings_file, 'rb') as f:
                    self.embeddings = pickle.load(f)
            except (IOError, pickle.UnpicklingError):
                self.embeddings = {}
    
    def _save_data(self):
        """Save embeddings và metadata"""
        # Save metadata
        try:
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, ensure_ascii=False, indent=2)
        except IOError as e:
            print(f"Error saving metadata: {e}")
        
        # Save embeddings
        try:
            with open(self.embeddings_file, 'wb') as f:
                pickle.dump(self.embeddings, f)
        except IOError as e:
            print(f"Error saving embeddings: {e}")
    
    def _simple_embedding(self, text: str) -> np.ndarray:
        """
        Simple embedding function (TF-IDF based hoặc có thể dùng sentence-transformers)
        Nếu có sentence-transformers, nên dùng model như 'paraphrase-multilingual-MiniLM-L12-v2'
        """
        # Fallback: Simple hash-based embedding (nên thay bằng proper embedding model)
        import hashlib
        
        # Tạo embedding đơn giản từ hash
        hash_obj = hashlib.sha256(text.encode('utf-8'))
        hash_bytes = hash_obj.digest()
        
        # Chuyển thành vector (hash_bytes có 32 bytes, mỗi float32 cần 4 bytes -> tối đa 8 floats)
        # Luôn dùng toàn bộ hash_bytes để tạo base embedding
        base_embedding = np.frombuffer(hash_bytes, dtype=np.float32)  # 32 bytes / 4 = 8 floats
        embedding_len = int(base_embedding.shape[0]) if hasattr(base_embedding, 'shape') else int(len(base_embedding))
        
        # Đảm bảo embedding_dim là int
        embedding_dim = int(self.embedding_dim)
        
        # Nếu embedding_dim <= số floats có thể tạo từ hash, chỉ lấy phần cần
        if embedding_dim <= embedding_len:
            embedding = base_embedding[:embedding_dim]
        else:
            # Nếu cần nhiều hơn, repeat base_embedding
            if embedding_len > 0:
                repeat_times = (embedding_dim // embedding_len) + 1
                embedding = np.tile(base_embedding, repeat_times)[:embedding_dim]
            else:
                # Fallback: tạo embedding zeros nếu có lỗi
                embedding = np.zeros(embedding_dim, dtype=np.float32)
        
        # Normalize
        
        # Normalize
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm
        
        return embedding
    
    def store(
        self,
        content: str,
        content_type: str,
        metadata: Optional[Dict[str, Any]] = None,
        content_id: Optional[str] = None
    ) -> str:
        """
        Lưu content với embedding
        Returns: content_id
        """
        if content_id is None:
            content_id = f"{content_type}_{datetime.now().timestamp()}_{hash(content) % 10000}"
        
        # Tạo embedding
        embedding = self._simple_embedding(content)
        
        # Lưu embedding
        self.embeddings[content_id] = embedding
        
        # Lưu metadata
        self.metadata[content_id] = {
            "content": content,
            "content_type": content_type,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        # Auto-save (có thể optimize bằng batch saving)
        self._save_data()
        
        return content_id
    
    def search(
        self,
        query: str,
        content_type: Optional[str] = None,
        top_k: int = 5,
        threshold: float = 0.5
    ) -> List[Dict[str, Any]]:
        """
        Tìm kiếm semantic similarity
        Returns: List of results với similarity scores
        """
        # Tạo embedding cho query
        query_embedding = self._simple_embedding(query)
        
        results = []
        
        # Tính similarity với tất cả embeddings
        for content_id, embedding in self.embeddings.items():
            # Check content type filter
            if content_type and self.metadata.get(content_id, {}).get("content_type") != content_type:
                continue
            
            # Cosine similarity
            similarity = np.dot(query_embedding, embedding)
            
            if similarity >= threshold:
                metadata = self.metadata.get(content_id, {})
                results.append({
                    "content_id": content_id,
                    "content": metadata.get("content", ""),
                    "content_type": metadata.get("content_type", ""),
                    "similarity": float(similarity),
                    "metadata": metadata.get("metadata", {})
                })
        
        # Sort by similarity
        results.sort(key=lambda x: x["similarity"], reverse=True)
        
        return results[:top_k]
    
    def search_by_embedding(
        self,
        query_embedding: np.ndarray,
        content_type: Optional[str] = None,
        top_k: int = 5,
        threshold: float = 0.5
    ) -> List[Dict[str, Any]]:
        """Tìm kiếm bằng embedding vector"""
        results = []
        
        for content_id, embedding in self.embeddings.items():
            if content_type and self.metadata.get(content_id, {}).get("content_type") != content_type:
                continue
            
            similarity = np.dot(query_embedding, embedding)
            
            if similarity >= threshold:
                metadata = self.metadata.get(content_id, {})
                results.append({
                    "content_id": content_id,
                    "content": metadata.get("content", ""),
                    "content_type": metadata.get("content_type", ""),
                    "similarity": float(similarity),
                    "metadata": metadata.get("metadata", {})
                })
        
        results.sort(key=lambda x: x["similarity"], reverse=True)
        return results[:top_k]
    
    def get_embedding(self, content_id: str) -> Optional[np.ndarray]:
        """Lấy embedding của content"""
        return self.embeddings.get(content_id)
    
    def delete(self, content_id: str):
        """Xóa content"""
        if content_id in self.embeddings:
            del self.embeddings[content_id]
        if content_id in self.metadata:
            del self.metadata[content_id]
        self._save_data()
    
    def get_stats(self) -> Dict[str, Any]:
        """Lấy statistics"""
        content_types = {}
        for metadata in self.metadata.values():
            content_type = metadata.get("content_type", "unknown")
            content_types[content_type] = content_types.get(content_type, 0) + 1
        
        return {
            "total_items": len(self.embeddings),
            "content_types": content_types,
            "embedding_dim": self.embedding_dim
        }
