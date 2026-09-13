"""Structured Output and Tool Accuracy Evaluator."""
class Evaluator:
    def compute_accuracy(self, generated_classes: list[str], expected_classes: list[str]) -> float:
        if not expected_classes:
            return 1.0
        matches = set(generated_classes).intersection(set(expected_classes))
        return len(matches) / len(expected_classes)
