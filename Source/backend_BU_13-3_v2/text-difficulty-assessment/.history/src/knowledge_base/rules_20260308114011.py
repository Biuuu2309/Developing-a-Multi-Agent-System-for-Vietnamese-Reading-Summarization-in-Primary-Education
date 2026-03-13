# src/knowledge_base/rules.py

class Rules:

    RULES = [

        # Grade 1
        {
            "name": "grade1_simple_text",
            "condition": lambda f: (
                f["avg_sentence_length"] <= 10 and
                f["rare_word_ratio"] < 0.05 and
                f["avg_word_grade"] <= 1.5
            ),
            "difficulty": 1
        },

        # Grade 2
        {
            "name": "grade2_basic_text",
            "condition": lambda f: (
                f["avg_sentence_length"] <= 13 and
                f["avg_word_grade"] <= 2.0
            ),
            "difficulty": 2
        },

        # Grade 3
        {
            "name": "grade3_medium_text",
            "condition": lambda f: (
                f["avg_sentence_length"] <= 15 and
                f["rare_word_ratio"] < 0.15
            ),
            "difficulty": 3
        },

        # Grade 4
        {
            "name": "grade4_complex_text",
            "condition": lambda f: (
                f["avg_sentence_length"] > 16 or
                f["rare_word_ratio"] >= 0.15
            ),
            "difficulty": 4
        },

        # Grade 5
        {
            "name": "grade5_very_complex",
            "condition": lambda f: (
                f["avg_sentence_length"] > 19 or
                f["unknown_word_ratio"] > 0.20
            ),
            "difficulty": 5
        }
    ]
