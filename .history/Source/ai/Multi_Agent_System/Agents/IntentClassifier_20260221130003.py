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

        self.prompt = ChatPromptTemplate.from_messages([
            ("system",
             "Bạn là hệ thống phân loại ý định.\n"
             "Trả về JSON hợp lệ theo cấu trúc sau:\n\n"
             "{{\n"
             '  "intent": one of ["summarize","evaluate","explain_system","casual_chat","image_analysis","unknown"],\n'
             '  "summarization_type": "abstractive" | "extractive" | null,\n'
             '  "grade_level": integer | null\n'
             "}}\n\n"
             "Chỉ trả về JSON. Không giải thích."),
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