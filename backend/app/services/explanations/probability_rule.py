from .base_rule import Explanation


class ProbabilityRule:
    """Flags high model confidence based on the Random Forest's own predicted probability."""

    def evaluate(self, transaction: dict, stats: dict) -> list[Explanation]:
        probability = transaction.get("fraud_probability")

        if probability is None:
            return []

        if probability >= 0.9:
            return [Explanation(reason="Strong Model Confidence", severity="high")]
        if probability >= 0.7:
            return [Explanation(reason="Moderate Model Confidence", severity="medium")]

        return []
