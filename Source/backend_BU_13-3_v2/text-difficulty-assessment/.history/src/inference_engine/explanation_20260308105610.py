# src/inference_engine/explanation.py


class ExplanationGenerator:

    def __init__(self):
        pass

    def generate(self, difficulty, features, matched_rules):

        explanation = []

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
