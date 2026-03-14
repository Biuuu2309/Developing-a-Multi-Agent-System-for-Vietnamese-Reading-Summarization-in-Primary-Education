# src/inference_engine/explanation.py


class ExplanationGenerator:

    def __init__(self):
        pass

    def generate(self, difficulty, features, matched_rules):

        explanation = []

        if difficulty == 0:
            explanation.append(
                "Hệ thống phát hiện văn bản chứa nhiều từ không có trong từ điển (có thể sai chính tả hoặc không phải tiếng Việt)."
            )
            explanation.append(
                "Vui lòng kiểm tra lại chính tả hoặc đảm bảo văn bản là tiếng Việt trước khi đánh giá."
            )
        else:
            explanation.append(f"Predicted difficulty level: Grade {difficulty}")
        explanation.append("")

        explanation.append("Feature summary:")

        for k, v in features.items():

            if isinstance(v, float):
                v = round(v, 3)

            explanation.append(f" - {k}: {v}")

        explanation.append("")
        explanation.append("Matched rules:")

        for r in matched_rules:
            explanation.append(f" - {r['name']}")

        return "\n".join(explanation)
