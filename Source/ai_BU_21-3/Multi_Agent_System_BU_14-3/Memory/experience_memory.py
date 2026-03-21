# experience_memory.py

from typing import List, Dict, Any
from datetime import datetime
from uuid import uuid4
import chromadb
from chromadb.config import Settings


class ExperienceMemory:
    """
    Long-term retrieval-based memory using ChromaDB.
    Stores summarization experiences for MAS learning.
    """

    def __init__(
        self,
        collection_name: str = "mas_experiences",
        persist_directory: str = "./chroma_db"
    ):
        self.client = chromadb.Client(
            Settings(
                persist_directory=persist_directory,
                is_persistent=True
            )
        )

        self.collection = self.client.get_or_create_collection(
            name=collection_name
        )

    # =========================================
    # Add Experience
    # =========================================
    def add_experience(self, input_text, summary_output, strategy, grade=None, confidence=None):
    
        metadata = {
            "strategy": strategy,
            "timestamp": datetime.now().isoformat()
        }
    
        if grade is not None:
            metadata["grade"] = int(grade)
    
        if confidence is not None:
            metadata["confidence"] = float(confidence)
    
        self.collection.add(
            documents=[input_text],
            metadatas=[metadata],
            ids=[uuid4().hex]
        )

    # =========================================
    # Retrieval
    # =========================================
    def search_similar_experiences(
        self,
        input_text: str,
        top_k: int = 3
    ) -> List[Dict[str, Any]]:

        results = self.collection.query(
            query_texts=[input_text],
            n_results=top_k
        )

        experiences = []

        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        for doc, meta, dist in zip(documents, metadatas, distances):
            experiences.append({
                "input_text": doc,
                "metadata": meta,
                "distance": dist
            })

        return experiences

    # =========================================
    # Strategy Statistics
    # =========================================
    def get_strategy_statistics(self) -> Dict[str, Any]:

        results = self.collection.get(include=["metadatas"])
        metadatas = results.get("metadatas", [])

        stats = {}

        for meta in metadatas:
            strategy = meta.get("strategy")
            confidence = meta.get("confidence", 0)

            if strategy not in stats:
                stats[strategy] = {
                    "count": 0,
                    "avg_confidence": 0
                }

            stats[strategy]["count"] += 1
            stats[strategy]["avg_confidence"] += confidence

        for strategy in stats:
            stats[strategy]["avg_confidence"] /= stats[strategy]["count"]

        return stats


# Shared singleton
experience_memory = ExperienceMemory()