"""
Central registry of explanation rules.

To add a new rule (Device, Merchant, Velocity, Geographical, Time...):
1. Create a new file in this package implementing ExplanationRule.
2. Import it below and add an instance to RULES.
No other file needs to change.
"""

from .base_rule import ExplanationRule, Explanation
from .amount_rule import AmountRule
from .country_rule import CountryRule
from .probability_rule import ProbabilityRule
from .pca_rule import PcaRule

RULES: list[ExplanationRule] = [
    AmountRule(),
    CountryRule(),
    ProbabilityRule(),
    PcaRule(),
]

SEVERITY_ORDER = {"high": 0, "medium": 1, "low": 2, "info": 3}


def run_rules(transaction: dict, stats: dict) -> list[Explanation]:
    """
    Executes every registered rule against the transaction, merges results,
    removes duplicate reasons, and sorts by severity (high first).
    """
    all_explanations: list[Explanation] = []

    for rule in RULES:
        try:
            all_explanations.extend(rule.evaluate(transaction, stats))
        except Exception:
            # A single failing rule must never break the others.
            continue

    seen_reasons = set()
    unique_explanations = []
    for exp in all_explanations:
        if exp.reason not in seen_reasons:
            seen_reasons.add(exp.reason)
            unique_explanations.append(exp)

    unique_explanations.sort(key=lambda e: SEVERITY_ORDER.get(e.severity, 99))

    return unique_explanations
