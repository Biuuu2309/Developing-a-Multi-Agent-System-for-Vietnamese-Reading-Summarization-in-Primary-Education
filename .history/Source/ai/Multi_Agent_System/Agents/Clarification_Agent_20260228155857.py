class ClarificationAgent:
    
    def __init__(self):
        pass

    def analyze(self, user_input: str, intent_result: dict, history: list = None) -> dict:
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
        # Truyền history để tìm văn bản đã được cung cấp trước đó
        if not self._has_text_content(user_input, intent_result, history):
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
        user_lower = user_input.lower().strip()

        # Kiểm tra strategy - hỗ trợ nhiều cách trả lời
        if any(keyword in user_lower for keyword in ["trích xuất", "extract", "extractive"]):
            intent_result["summarization_type"] = "extractive"
        elif any(keyword in user_lower for keyword in ["diễn giải", "abstract", "abstractive"]):
            intent_result["summarization_type"] = "abstractive"

        # Kiểm tra grade_level - hỗ trợ nhiều format
        import re
        # Format: "lớp 1", "lớp1", "lớp 5"
        grade_match = re.search(r'lớp\s*(\d+)', user_lower)
        if grade_match:
            intent_result["grade_level"] = int(grade_match.group(1))
        else:
            # Format: chỉ số đơn lẻ (1-5) nếu input ngắn
            if len(user_lower.split()) <= 2:
                single_digit = re.search(r'^(\d)$', user_lower.strip())
                if single_digit:
                    grade = int(single_digit.group(1))
                    if 1 <= grade <= 5:
                        intent_result["grade_level"] = grade

        return intent_result

    def _has_text_content(self, user_input: str, _intent_result: dict, history: list = None) -> bool:
        """
        Kiểm tra xem user_input có chứa văn bản cần tóm tắt không
        (không phải chỉ là câu hỏi hoặc yêu cầu)
        Nếu không tìm thấy trong user_input, tìm trong history
        """
        user_lower = user_input.lower().strip()
        
        # Nếu input quá ngắn (< 50 ký tự), có thể chỉ là câu trả lời
        # Nhưng trước tiên kiểm tra xem có văn bản trong history không
        if len(user_lower) < 50:
            # Kiểm tra history trước khi return False
            if history:
                for msg in reversed(history):
                    if msg.get("role") == "user":
                        content = msg.get("content", "")
                        content_lower = content.lower()
                        # Nếu có văn bản dài trong history (có thể là text đã cung cấp)
                        if len(content.strip()) > 100:
                            # Kiểm tra xem có phải là văn bản thực sự không
                            word_count = len(content.split())
                            sentence_count = content.count('.') + content.count('!') + content.count('?')
                            # Nếu có nhiều từ (> 20) hoặc nhiều câu (> 1) và không chỉ là câu trả lời ngắn
                            if (word_count > 20 or sentence_count > 1) and not any(
                                kw in content_lower[:50] for kw in 
                                ["trích xuất", "diễn giải", "extract", "abstract", "tôi muốn", "lớp"]
                            ):
                                return True
            return False

        # Loại bỏ các câu trả lời ngắn chỉ về strategy/grade
        short_responses = [
            "trích xuất", "extract", "extractive",
            "diễn giải", "abstract", "abstractive",
            "lớp 1", "lớp 2", "lớp 3", "lớp 4", "lớp 5",
            "1", "2", "3", "4", "5"
        ]
        if user_lower in short_responses or len(user_lower.split()) <= 3:
            # Kiểm tra history trước khi return False
            if history:
                for msg in reversed(history):
                    if msg.get("role") == "user":
                        content = msg.get("content", "")
                        if len(content.strip()) > 100:
                            word_count = len(content.split())
                            sentence_count = content.count('.') + content.count('!') + content.count('?')
                            if (word_count > 20 or sentence_count > 1):
                                content_lower = content.lower()
                                # Không phải là câu trả lời ngắn về strategy/grade
                                if not any(kw in content_lower[:50] for kw in 
                                          ["trích xuất", "diễn giải", "extract", "abstract", "tôi muốn"]):
                                    return True
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
                # Kiểm tra history
                if history:
                    for msg in reversed(history):
                        if msg.get("role") == "user":
                            content = msg.get("content", "")
                            if len(content.strip()) > 100:
                                word_count = len(content.split())
                                sentence_count = content.count('.') + content.count('!') + content.count('?')
                                if (word_count > 20 or sentence_count > 1):
                                    return True
                return False

        # Nếu có nhiều câu (dấu chấm) hoặc nhiều từ, có thể là văn bản
        sentence_count = user_lower.count('.') + user_lower.count('!') + user_lower.count('?')
        word_count = len(user_lower.split())
        
        # Nếu có ít nhất 2 câu hoặc nhiều hơn 20 từ, có thể là văn bản
        if sentence_count >= 2 or word_count >= 20:
            return True
        
        # Nếu input dài (> 100 ký tự) và không phải là câu trả lời ngắn
        if len(user_lower) > 100:
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