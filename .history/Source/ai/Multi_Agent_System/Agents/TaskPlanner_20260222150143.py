from typing import TypedDict, Literal, Optional


class TaskDefinition(TypedDict):
    task_type: Literal[
        "summarization",
        "evaluation",
        "explain_system",
        "casual_chat",
        "image_analysis",
        "unknown"
    ]
    strategy: Optional[Literal["abstractive", "extractive"]]
    grade_level: Optional[int]
    
class TaskPlanner:
    
    def plan(self, intent_result: dict) -> TaskDefinition:

        intent = intent_result.get("intent", "unknown")
        summarization_type = intent_result.get("summarization_type")
        grade_level = intent_result.get("grade_level")

        # =========================
        # Summarization
        # =========================

        if intent == "summarize":

            strategy = summarization_type or "abstractive"

            return {
                "task_type": "summarization",
                "strategy": strategy,
                "grade_level": grade_level
            }

        # =========================
        # Evaluation
        # =========================

        if intent == "evaluate":
            return {
                "task_type": "evaluation",
                "strategy": None,
                "grade_level": None
            }

        # =========================
        # Explain system
        # =========================

        if intent == "explain_system":
            return {
                "task_type": "explain_system",
                "strategy": None,
                "grade_level": None
            }

        # =========================
        # Casual chat
        # =========================

        if intent == "casual_chat":
            return {
                "task_type": "casual_chat",
                "strategy": None,
                "grade_level": None
            }

        # =========================
        # Image analysis
        # =========================

        if intent == "image_analysis":
            return {
                "task_type": "image_analysis",
                "strategy": None,
                "grade_level": None
            }

        # =========================
        # Fallback
        # =========================

        return {
            "task_type": "unknown",
            "strategy": None,
            "grade_level": None
        }