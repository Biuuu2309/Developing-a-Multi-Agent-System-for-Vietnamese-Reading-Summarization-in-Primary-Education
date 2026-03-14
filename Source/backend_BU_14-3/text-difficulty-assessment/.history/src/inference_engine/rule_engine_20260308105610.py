# src/inference_engine/rule_engine.py

from knowledge_base.rules import Rules


class RuleEngine:

    def __init__(self):
        self.rules = Rules.RULES

    def infer(self, features):
        """
        Run rule-based inference
        """
        matched_rules = []

        for rule in self.rules:

            try:
                if rule["condition"](features):
                    matched_rules.append(rule)

            except KeyError:
                continue

        if not matched_rules:
            return None, []

        # chọn rule difficulty cao nhất
        best_rule = max(matched_rules, key=lambda r: r["difficulty"])

        return best_rule["difficulty"], matched_rules
