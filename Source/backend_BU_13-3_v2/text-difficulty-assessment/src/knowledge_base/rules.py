# src/knowledge_base/rules.py

class Rules:

    RULES = [

        # Invalid input: quá nhiều từ không nằm trong từ điển
        {
            "name": "invalid_input_too_many_unknown_words",
            "condition": lambda f: (
                f.get("unknown_word_ratio", 0) >= 0.20
            ),
            "difficulty": 0
        },

        # Grade 1 - Mở rộng điều kiện để dễ match hơn
        {
            "name": "grade1_simple_text",
            "condition": lambda f: (
                f["avg_sentence_length"] <= 12 and
                f["rare_word_ratio"] < 0.10 and
                f["avg_word_grade"] <= 2.0 and
                f["unknown_word_ratio"] < 0.10
            ),
            "difficulty": 1
        },

        # Grade 2 - Mở rộng điều kiện
        {
            "name": "grade2_basic_text",
            "condition": lambda f: (
                f["avg_sentence_length"] <= 15 and
                f["avg_word_grade"] <= 2.5 and
                f["rare_word_ratio"] < 0.12
            ),
            "difficulty": 2
        },

        # Grade 3 - Tăng ngưỡng để khó match hơn
        {
            "name": "grade3_medium_text",
            "condition": lambda f: (
                f["avg_sentence_length"] > 15 and
                f["avg_sentence_length"] <= 18 and
                f["rare_word_ratio"] >= 0.12 and
                f["rare_word_ratio"] < 0.20
            ),
            "difficulty": 3
        },

        # Grade 4 - Tăng ngưỡng
        {
            "name": "grade4_complex_text",
            "condition": lambda f: (
                (f["avg_sentence_length"] > 18 and f["avg_sentence_length"] <= 22) or
                (f["rare_word_ratio"] >= 0.20 and f["rare_word_ratio"] < 0.30)
            ),
            "difficulty": 4
        },

        # Grade 5 - Chỉ khi rất phức tạp
        {
            "name": "grade5_very_complex",
            "condition": lambda f: (
                f["avg_sentence_length"] > 22 or
                f["rare_word_ratio"] >= 0.30 or
                f["unknown_word_ratio"] > 0.25
            ),
            "difficulty": 5
        }
    ]
