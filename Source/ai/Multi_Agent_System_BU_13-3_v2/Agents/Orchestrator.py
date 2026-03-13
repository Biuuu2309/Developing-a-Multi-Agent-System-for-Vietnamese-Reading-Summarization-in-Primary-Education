from typing import Optional
from Source.ai.Multi_Agent_System.Memory.experience_memory import ExperienceMemory


class Orchestrator:
    """
    Execution Orchestrator for System 1.
    Pure routing logic between Extractor and Abstracter.
    No conversation logic.
    No LLM decision.
    No LangGraph.
    """

    def __init__(self, abstracter_agent, extractor_agent):
        self.abstracter = abstracter_agent
        self.extractor = extractor_agent
        self.experience_memory = ExperienceMemory()

    # ==========================================
    # Strategy Selection (Deterministic)
    # ==========================================

    def _select_strategy(self, user_input: str) -> str:
        """
        Select summarization strategy based on keywords
        or fallback to experience memory.
        """

        user_input_lower = user_input.lower()

        if "trích xuất" in user_input_lower:
            return "extractive"

        if "diễn giải" in user_input_lower:
            return "abstractive"

        # Fallback: use experience memory (optional)
        similar_cases = self.experience_memory.search_similar_experiences(
            user_input,
            top_k=1
        )

        if similar_cases:
            metadata = similar_cases[0].get("metadata", {})
            return metadata.get("strategy", "abstractive")

        # Default strategy
        return "abstractive"

    # ==========================================
    # Main Execution
    # ==========================================
    def run(
        self,
        user_input: str,
        strategy: str = None,
        grade_level: int = None,
        length_option: str = "medium",
    ):
        """
        Thực thi tóm tắt với chiến lược đã chọn.
        - Extractive: bỏ qua length_option, dùng ratio cố định.
        - Abstractive: truyền length_option xuống AbstracterAgent
          để điều khiển độ dài (short / medium / long).
        """
        if strategy == "extractive":
            return self.extractor.run(user_input, ratio=0.5)

        if grade_level is None:
            grade_level = 5

        return self.abstracter.run(
            content=user_input,
            grade=grade_level,
            mode="sample",
            length_option=length_option or "medium",
        )