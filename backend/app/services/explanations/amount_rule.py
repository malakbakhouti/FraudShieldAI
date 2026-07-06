from .base_rule import Explanation


class AmountRule:
    """Flags transactions whose amount exceeds the dataset's 95th percentile."""

    def evaluate(self, transaction: dict, stats: dict) -> list[Explanation]:
        amount = transaction.get("amount")
        p95 = stats.get("amount_p95")

        if amount is None or not p95:
            return []

        if amount > p95:
            return [Explanation(reason="Unusually High Transaction Amount", severity="medium")]

        return []
