# src/knowledge_base/difficulty_levels.py

class DifficultyLevels:

    LEVELS = {
        0: "Văn bản không hợp lệ (nhiều từ không có trong từ điển, vui lòng kiểm tra chính tả hoặc đảm bảo là tiếng Việt)",
        1: "Grade 1",
        2: "Grade 2",
        3: "Grade 3",
        4: "Grade 4",
        5: "Grade 5"
    }

    @staticmethod
    def get_label(level):
        return DifficultyLevels.LEVELS.get(level, "Unknown")

    @staticmethod
    def all_levels():
        return list(DifficultyLevels.LEVELS.keys())
