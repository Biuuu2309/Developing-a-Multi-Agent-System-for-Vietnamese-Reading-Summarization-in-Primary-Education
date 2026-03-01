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
        "image_ocr",
        "unknown"
    ]
    summarization_type: Optional[Literal["abstractive", "extractive"]]
    grade_level: Optional[int]


class IntentAgent:

    def __init__(self):
        self.llm = ChatOllama(model="qwen2.5:7b")

        system_prompt = (
            "Bạn là hệ thống phân loại ý định. "
            "Trả về JSON hợp lệ với các trường:\n"
            '- intent: một trong ["summarize", "evaluate", "explain_system", "casual_chat", "image_analysis", "image_ocr", "unknown"]\n'
            '- summarization_type: "abstractive" nếu có từ "diễn giải", "extractive" nếu có từ "trích xuất", null nếu không rõ\n'
            '- grade_level: trích xuất số lớp từ input (ví dụ: "lớp 1" = 1, "lớp 5" = 5), null nếu không có\n\n'
            "Quan trọng: Nếu input có từ 'diễn giải' thì summarization_type phải là 'abstractive'. "
            "Nếu input có từ 'trích xuất' thì summarization_type phải là 'extractive'.\n"
            "Nếu input có đường dẫn ảnh (jpg, png, etc.) hoặc từ khóa 'ảnh', 'image', 'hình' và user muốn trích xuất text, intent là 'image_ocr'.\n"
            "Nếu user muốn tóm tắt từ ảnh, intent là 'summarize' với image_path.\n"
            "Chỉ trả về JSON. Không giải thích."
        )
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{user_input}")
        ])

    def classify(self, user_input: str = None, history: list = None, **kwargs) -> IntentResult:
        """
        Classify user intent from input.
        
        Args:
            user_input: User input string (can be passed as positional or keyword arg)
            history: Optional conversation history
            **kwargs: Additional keyword arguments (for compatibility)
        """
        # Handle both positional and keyword arguments
        if user_input is None:
            user_input = kwargs.get("user_input", "")
        
        if history is None:
            history = kwargs.get("history", [])

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