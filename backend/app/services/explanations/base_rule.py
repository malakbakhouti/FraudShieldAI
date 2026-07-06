"""
Common interface for all explanation rules.

Each rule inspects a transaction (amount, country, features, fraud_probability)
against the dynamic statistics computed by DataStatsProvider, and returns zero
or more Explanation objects. Rules are self-contained: adding a new rule never
requires touching existing rules or the aggregator's merge/sort logic.
"""

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class Explanation:
    reason: str
    severity: str  # "info" | "low" | "medium" | "high"


class ExplanationRule(Protocol):
    """
    Any explanation rule must implement evaluate().

    `transaction` is a dict with at least: amount, country, features (dict), fraud_probability.
    `stats` is the dict returned by data_stats.get_data_stats().
    """

    def evaluate(self, transaction: dict, stats: dict) -> list[Explanation]:
        ...
