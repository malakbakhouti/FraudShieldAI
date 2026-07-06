"""
CountryRateFactor: scores country risk based on how far a country's fraud
rate deviates from the global fraud rate, using a sigmoid function whose
center and slope are calibrated dynamically from the real, current
distribution of country ratios (see DataStatsProvider.country_ratio_distribution).

Why a sigmoid, and why dynamically calibrated:
- A hardcoded log-curve scale (or any fixed threshold) saturates the score
  near 100 for any ratio past a fixed point, making genuinely different risk
  levels (e.g. 10x vs 15x vs 20x) indistinguishable.
- Centering the sigmoid on the *median* observed ratio means a country at
  "typical" relative risk always scores 50, regardless of how the overall
  fraud landscape shifts after new imports.
- Deriving the slope from the interquartile spread means the curve
  automatically stretches to fit the real variability in the data: a widely
  spread distribution produces a gentler curve, a tightly clustered one
  produces a steeper curve, without any manual re-tuning.
"""

import math

from .base_factor import CountryFactor
from .models import FactorResult
from app.config import settings

FACTOR_NAME = "CountryRateFactor"

# Sample size at which confidence is considered "full" (1.0). Below this,
# confidence scales down linearly toward a floor. This is a statistical
# reliability parameter, not a risk threshold.
CONFIDENCE_FULL_SAMPLE_SIZE = 200
CONFIDENCE_FLOOR = 0.3

# Target sigmoid value at one spread-width away from the center, used to
# derive the slope from the spread. 0.9 means: a country one interquartile
# spread above the median reaches ~90/100, a smooth, non-arbitrary anchor
# point for translating "spread" into "steepness".
_SIGMOID_TARGET_AT_ONE_SPREAD = 0.9


def _sigmoid_slope_from_spread(spread: float) -> float:
    """
    Derives the logistic slope k such that sigmoid(center + spread) ==
    _SIGMOID_TARGET_AT_ONE_SPREAD, given sigmoid(x) = 1 / (1 + exp(-k*(x-center))).

    Solving for k: k = ln(target / (1 - target)) / spread
    """
    target = _SIGMOID_TARGET_AT_ONE_SPREAD
    logit = math.log(target / (1 - target))
    return logit / spread if spread > 0 else 0.0


class CountryRateFactor(CountryFactor):
    """Scores a transaction's country based on its relative fraud rate vs. the global baseline."""

    def score(self, transaction: dict, stats: dict) -> FactorResult:
        weight = settings.country_rate_factor_weight
        country = transaction.get("country")
        country_stats = stats.get("country_stats", {})
        global_rate = stats.get("global_fraud_rate", 0.0)
        distribution = stats.get("country_ratio_distribution", {"median": 1.0, "spread": 1.0, "sample_countries": 0})

        if not country or country not in country_stats or global_rate <= 0:
            return FactorResult(
                factor_name=FACTOR_NAME,
                score=0.0,
                weight=weight,
                weighted_score=0.0,
                details="Insufficient data to assess country fraud rate.",
                confidence=0.0,
            )

        entry = country_stats[country]
        country_rate = entry["rate"]
        sample_size = entry["total"]

        ratio = country_rate / global_rate if global_rate > 0 else 0.0

        center = distribution.get("median", 1.0)
        spread = distribution.get("spread", 1.0)
        slope = _sigmoid_slope_from_spread(spread)

        if slope <= 0:
            score = 0.0
        else:
            try:
                score = 100.0 / (1.0 + math.exp(-slope * (ratio - center)))
            except OverflowError:
                score = 100.0 if ratio > center else 0.0

        score = max(0.0, min(100.0, score))

        confidence = min(1.0, max(CONFIDENCE_FLOOR, sample_size / CONFIDENCE_FULL_SAMPLE_SIZE))

        details = (
            f"Country fraud rate is {country_rate * 100:.2f}%. "
            f"Global fraud rate is {global_rate * 100:.2f}%. "
            f"Relative risk = {ratio:.1f}x (median across {distribution.get('sample_countries', 0)} "
            f"tracked countries = {center:.1f}x, based on {sample_size} transactions)."
        )

        return FactorResult(
            factor_name=FACTOR_NAME,
            score=round(score, 2),
            weight=weight,
            weighted_score=round(score * weight, 2),
            details=details,
            confidence=round(confidence, 2),
        )
