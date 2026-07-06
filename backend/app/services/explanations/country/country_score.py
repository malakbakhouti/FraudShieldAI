"""
CountryScoreEngine: combines all registered CountryFactor results into a
single, weighted CountryScore for a transaction.

Design principles:
- Each factor runs independently; a failing factor is logged and skipped,
  never crashes the engine or affects other factors.
- The final score is a confidence-weighted average: each factor's
  contribution is scaled by (weight * confidence), not weight alone. This is
  generic and applies automatically to every registered factor, present and
  future (TrendFactor, VelocityFactor, MerchantFactor, ...) without any
  factor needing to implement this logic itself. A factor that reports low
  confidence (e.g. SampleSizeFactor on a thin sample) naturally contributes
  less to the final blended score, exactly mirroring how a human analyst
  would discount an unreliable signal rather than ignoring it outright or
  trusting it fully.
- Severity thresholds are fixed business rules (0-39 low, 40-69 medium,
  70-100 high) applied uniformly regardless of which factors are active.
"""

import logging
from dataclasses import replace

from .models import FactorResult, CountryScore
from .factor_registry import FactorRegistry

logger = logging.getLogger("country_score_engine")

SEVERITY_LOW_MAX = 39
SEVERITY_MEDIUM_MAX = 69


def _severity_from_score(score: float) -> str:
    if score <= SEVERITY_LOW_MAX:
        return "low"
    if score <= SEVERITY_MEDIUM_MAX:
        return "medium"
    return "high"


def _effective_weight(result: FactorResult) -> float:
    """
    Computes the confidence-adjusted weight for a single factor result.

    This is the single place where "confidence discounts contribution" is
    implemented, so every current and future factor benefits automatically
    without duplicating this logic.
    """
    return result.weight * result.confidence


class CountryScoreEngine:
    """
    Runs all factors from a FactorRegistry against a transaction and produces
    a single aggregated CountryScore.
    """

    def __init__(self, registry: FactorRegistry | None = None):
        self._registry = registry or FactorRegistry.default()

    def evaluate(self, transaction: dict, stats: dict) -> CountryScore:
        """
        Evaluates every registered factor for the given transaction and
        combines the results into a final weighted CountryScore.

        If no factors are registered, or all factors fail, returns a neutral
        CountryScore(final_score=0.0, severity="low") rather than raising.
        """
        raw_results: list[FactorResult] = []

        for factor in self._registry.all():
            factor_name = type(factor).__name__
            try:
                result = factor.score(transaction, stats)
                raw_results.append(result)
            except Exception as e:
                logger.error(
                    f"[country_score_engine] Factor '{factor_name}' failed, skipping. Error: {e}",
                    exc_info=True,
                )
                continue

        if not raw_results:
            return CountryScore(final_score=0.0, severity="low", factors=[], details=[])

        # Recompute weighted_score using the confidence-adjusted effective weight,
        # so FactorResult.weighted_score always reflects what actually counted
        # toward the final score (kept consistent for transparency/debugging).
        adjusted_results = [
            replace(r, weighted_score=round(r.score * _effective_weight(r), 2))
            for r in raw_results
        ]

        total_effective_weight = sum(_effective_weight(r) for r in raw_results)

        if total_effective_weight <= 0:
            final_score = 0.0
        else:
            final_score = sum(r.weighted_score for r in adjusted_results) / total_effective_weight

        final_score = max(0.0, min(100.0, final_score))
        severity = _severity_from_score(final_score)
        details = [r.details for r in adjusted_results if r.details]

        return CountryScore(
            final_score=round(final_score, 2),
            severity=severity,
            factors=adjusted_results,
            details=details,
        )
