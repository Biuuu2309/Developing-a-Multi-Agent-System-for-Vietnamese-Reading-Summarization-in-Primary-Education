class ClarificationAgent:
    
    def __init__(self):
        pass

    def analyze(self, user_input: str, intent_result: dict) -> dict:
        """
        Kiểm tra xem có cần hỏi lại user không
        """

        if intent_result.get("intent") != "summarize":
            return {"need_clarification": False}

        missing_fields = []

        if not intent_result.get("summarization_type"):
            missing_fields.append("summarization_type")

        if not intent_result.get("grade_level"):
            missing_fields.append("grade_level")

        if not user_input.strip():
            missing_fields.append("text")

        if missing_fields:
            question = self._build_question(missing_fields)

            return {
                "need_clarification": True,
                "missing_fields": missing_fields,
                "question": question
            }

        return {"need_clarification": False}

    def _build_question(self, missing_fields: list) -> str:

        questions = []

        if "summarization_type" in missing_fields:
            questions.append(
                "Bạn muốn tóm tắt văn bản theo dạng trích xuất hay diễn giải?"
            )

        if "grade_level" in missing_fields:
            questions.append(
                "Bạn muốn tóm tắt văn bản theo lớp mấy?"
            )

        if "text" in missing_fields:
            questions.append(
                "Bạn vui lòng cung cấp đoạn văn cần xử lý."
            )

        return " ".join(questions)