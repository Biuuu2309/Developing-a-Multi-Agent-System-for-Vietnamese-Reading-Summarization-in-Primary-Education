from typing import Optional
from typing import TypedDict, Literal
from langchain_community.chat_models import ChatOllama
from langchain.prompts import ChatPromptTemplate


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

        self.prompt = ChatPromptTemplate.from_messages([
            ("system",
             "Bạn là một hệ thống phân loại ý định.\n"
             "Hãy phân tích yêu cầu của người dùng và trả về JSON có cấu trúc:\n\n"
             "{\n"
             "  'intent': one of [summarize, evaluate, explain_system, casual_chat, image_analysis, unknown],\n"
             "  'summarization_type': abstractive | extractive | null,\n"
             "  'grade_level': integer | null\n"
             "}\n\n"
             "Chỉ trả về JSON hợp lệ. Không giải thích."),
            ("human", "{user_input}")
        ])

    def classify(self, user_input: str) -> IntentResult:

        chain = self.prompt | self.llm

        response = chain.invoke({"user_input": user_input}).content.strip()

        try:
            import json
            parsed = json.loads(response)
        except Exception:
            parsed = {
                "intent": "unknown",
                "summarization_type": None,
                "grade_level": None
            }

        return parsed