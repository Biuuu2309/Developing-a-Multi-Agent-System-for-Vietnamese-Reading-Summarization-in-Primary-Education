# long_term_memory.py
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import uuid
import os

class LongTermMemory:
    def __init__(self, persist_directory="./long_term_memory"):
        self.persist_directory = persist_directory
        os.makedirs(persist_directory, exist_ok=True)
        
        # Khởi tạo Chroma client
        self.client = chromadb.Client(Settings(
            persist_directory=persist_directory,
            is_persistent=True,
        ))
        
        # Tạo hoặc lấy collection
        self.collection = self.client.get_or_create_collection( #
            name="conversation_memory",
            metadata={"hnsw:space": "cosine"}
        )
        
        # Load embedding model (local, không cần API)
        self.embedder = SentenceTransformer('keepitreal/vietnamese-sbert', trust_remote_code=True) #
    
    def add_memory(self, session_id: str, role: str, content: str, metadata: dict = None): #
        """Lưu trữ một đoạn hội thoại vào long-term memory"""
        memory_id = str(uuid.uuid4())
        text_to_store = f"{role}: {content}"
        
        # Tạo embedding
        embedding = self.embedder.encode(text_to_store).tolist()
        
        # Metadata
        if metadata is None:
            metadata = {}
        metadata["session_id"] = session_id
        metadata["role"] = role
        
        # Thêm vào database
        self.collection.add(
            ids=[memory_id],
            embeddings=[embedding],
            documents=[text_to_store],
            metadatas=[metadata]
        )
    
    def retrieve_related_memories(self, query: str, session_id: str = None, limit: int = 3): #
        """Truy vấn các ký ức liên quan"""
        query_embedding = self.embedder.encode(query).tolist()
        
        # Xây dựng filter
        filter_dict = {}
        if session_id:
            filter_dict["session_id"] = session_id
        
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=limit,
            where=filter_dict if filter_dict else None
        )
        
        return results
    
    def get_conversation_context(self, current_query: str, session_id: str = None): #
        """Lấy ngữ cảnh từ long-term memory cho query hiện tại"""
        results = self.retrieve_related_memories(current_query, session_id)
        
        if not results or not results['documents']:
            return "Không có thông tin liên quan từ các cuộc trò chuyện trước."
        
        context = "Thông tin từ các cuộc trò chuyện trước:\n"
        for i, doc in enumerate(results['documents'][0]):
            context += f"{i+1}. {doc}\n"
        
        return context
    
    def clear_memory(self):
        """Xóa toàn bộ long-term memory"""
        self.client.delete_collection("conversation_memory")
        self.collection = self.client.get_or_create_collection(
            name="conversation_memory",
            metadata={"hnsw:space": "cosine"}
        )

# Singleton instance
long_term_memory = LongTermMemory()