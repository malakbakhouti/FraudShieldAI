"""
Shared data structures for the Country Risk Scoring Engine.

FactorResult is the output of a single CountryFactor.
CountryScore is the aggregated result of running all registered factors.
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class FactorResult:
    """
    The result of a single risk factor's evaluation for one transaction.

    Attributes:
        factor_name: Human-readable identifier of the factor (e.g. "CountryRateFactor").
        score: Raw risk score contributed by this factor, in the 0-100 range.
        weight: The configured weight applied to this factor (0.0-1.0), read
            from settings so it can be tuned without code changes.
        weighted_score: score * weight, precomputed for convenience.
        details: Human-readable explanation of why this score was given.
        confidence: How statistically reliable this factor's result is (0.0-1.0).
            Factors with low sample sizes should report low confidence rather
            than silently producing a misleading score.
    """
    factor_name: str
    score: float
    weight: float
    weighted_score: float
    details: str
    confidence: float


@dataclass(frozen=True)
class CountryScore:
    """
    The aggregated result of the Country Risk Scoring Engine for one transaction.

    Attributes:
        final_score: Weighted combination of all factor scores, 0-100.
        severity: One of "low" | "medium" | "high", derived from final_score.
        factors: Individual FactorResult objects that contributed to the score,
            preserved for transparency and debugging.
        details: Flattened list of human-readable explanations from all factors,
            ready to surface to an analyst.
    """
    final_score: float
    severity: str
    factors: list[FactorResult] = field(default_factory=list)
    details: list[str] = field(default_factory=list)
