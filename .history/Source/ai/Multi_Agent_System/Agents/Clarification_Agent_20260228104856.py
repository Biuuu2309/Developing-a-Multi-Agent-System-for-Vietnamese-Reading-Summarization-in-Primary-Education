class ClarificationAgent:
    
    def __init__(self):
        pass

    def analyze(self, user_input: str, intent_result: dict) -> dict:
        """
        Kiểm tra xem có cần hỏi lại user không
        """

        if intent_result.get("intent") != "summarize":
            return {"need_clarification": False}

        # Parse câu trả lời của user để cập nhật intent_result
        intent_result = self._parse_user_response(user_input, intent_result)

        missing_fields = []

        # Kiểm tra strategy
        if not intent_result.get("summarization_type"):
            missing_fields.append("summarization_type")
        else:
            # Chỉ kiểm tra grade_level nếu strategy là abstractive
            strategy = intent_result.get("summarization_type")
            if strategy == "abstractive" and not intent_result.get("grade_level"):
                missing_fields.append("grade_level")

        # Kiểm tra văn bản (chỉ khi đã có đủ thông tin strategy và grade_level nếu cần)
        if not self._has_text_content(user_input, intent_result):
            missing_fields.append("text")

        if missing_fields:
            question = self._build_question(missing_fields, intent_result)

            return {
                "need_clarification": True,
                "missing_fields": missing_fields,
                "question": question,
                "updated_intent": intent_result
            }

        # Ngay cả khi không cần clarification, vẫn trả về updated_intent
        # để lưu lại thông tin đã parse
        return {
            "need_clarification": False,
            "updated_intent": intent_result
        }

    def _parse_user_response(self, user_input: str, intent_result: dict) -> dict:
        """
        Parse câu trả lời của user để cập nhật intent_result
        """
        user_lower = user_input.lower()

        # Kiểm tra strategy
        if "trích xuất" in user_lower or "extract" in user_lower:
            intent_result["summarization_type"] = "extractive"
        elif "diễn giải" in user_lower or "abstract" in user_lower:
            intent_result["summarization_type"] = "abstractive"

        # Kiểm tra grade_level
        import re
        grade_match = re.search(r'lớp\s*(\d+)', user_lower)
        if grade_match:
            intent_result["grade_level"] = int(grade_match.group(1))

        return intent_result

    def _has_text_content(self, user_input: str, intent_result: dict) -> bool:
        """
        Kiểm tra xem user_input có chứa văn bản cần tóm tắt không
        (không phải chỉ là câu hỏi hoặc yêu cầu)
        """
        user_lower = user_input.lower().strip()
        
        # Nếu input quá ngắn (< 50 ký tự), có thể chỉ là câu trả lời
        if len(user_lower) < 50:
            return False

        # Loại bỏ các câu trả lời ngắn chỉ về strategy/grade
        short_responses = [
            "trích xuất", "extract", "extractive",
            "diễn giải", "abstract", "abstractive",
            "lớp 1", "lớp 2", "lớp 3", "lớp 4", "lớp 5"
        ]
        if user_lower in short_responses or len(user_lower.split()) <= 3:
            return False

        # Nếu input chỉ chứa các từ khóa về strategy/grade và không có văn bản thực sự
        strategy_keywords = ["trích xuất", "diễn giải", "extract", "abstract", "lớp", "grade"]
        text_indicators = ["văn bản", "đoạn", "bài", "nội dung", "sau", "đây"]
        
        # Nếu có từ khóa strategy nhưng không có indicator của văn bản
        has_strategy_keyword = any(kw in user_lower for kw in strategy_keywords)
        has_text_indicator = any(ind in user_lower for ind in text_indicators)
        
        # Nếu có strategy keyword nhưng không có text indicator và quá ngắn
        if has_strategy_keyword and not has_text_indicator:
            if len(user_lower.split()) < 15:
                return False

        # Nếu có nhiều câu (dấu chấm) hoặc nhiều từ, có thể là văn bản
        sentence_count = user_lower.count('.') + user_lower.count('!') + user_lower.count('?')
        word_count = len(user_lower.split())
        
        # Nếu có ít nhất 2 câu hoặc nhiều hơn 20 từ, có thể là văn bản
        if sentence_count >= 2 or word_count >= 20:
            return True

        return False

    def _build_question(self, missing_fields: list, intent_result: dict) -> str:

        questions = []

        # Chỉ hỏi strategy nếu chưa có
        if "summarization_type" in missing_fields:
            questions.append(
                "Bạn muốn tóm tắt văn bản theo dạng trích xuất hay diễn giải?"
            )

        # Chỉ hỏi grade_level nếu strategy là abstractive và chưa có
        if "grade_level" in missing_fields:
            strategy = intent_result.get("summarization_type")
            if strategy == "abstractive":
                questions.append(
                    "Bạn muốn tóm tắt văn bản theo lớp mấy?"
                )

        # Hỏi văn bản cuối cùng
        if "text" in missing_fields:
            questions.append(
                "Vui lòng cung cấp văn bản cần tóm tắt."
            )

        return " ".join(questions)