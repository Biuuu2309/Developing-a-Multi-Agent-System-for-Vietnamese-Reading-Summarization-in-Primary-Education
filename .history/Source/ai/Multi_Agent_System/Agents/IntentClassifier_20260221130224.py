from typing import Optional, TypedDict, Literal
from langchain_community.chat_models import ChatOllama
from langchain.prompts import ChatPromptTemplate
import json


class IntentResult(TypedDict):
    intent: Literal[
        "summarize",
        "evaluate",
        "explain_system",
        "casual_chat",
        "image_analysis",
        "unknown"
    ]
    summarization_type: Optional[Literal["abstractive", "extractive"]]
    grade_level: Optional[int]


class IntentClassifier:

    def __init__(self):
        self.llm = ChatOllama(model="qwen2.5:7b")

        system_prompt = (
            "Bạn là hệ thống phân loại ý định. "
            "Trả về JSON hợp lệ với các trường: "
            'intent (một trong: "summarize", "evaluate", "explain_system", "casual_chat", "image_analysis", "unknown"), '
            'summarization_type ("abstractive" hoặc "extractive" hoặc null), '
            'grade_level (số nguyên hoặc null). '
            "Chỉ trả về JSON. Không giải thích."
        )
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{user_input}")
        ])

    def classify(self, user_input: str) -> IntentResult:

        chain = self.prompt | self.llm
        response = chain.invoke({"user_input": user_input}).content.strip()

        # Clean markdown if model returns ```json
        response = response.replace("```json", "").replace("```", "").strip()

        try:
            parsed = json.loads(response)
        except Exception:
            parsed = {
                "intent": "unknown",
                "summarization_type": None,
                "grade_level": None
            }

        return parsed