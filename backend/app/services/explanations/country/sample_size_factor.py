"""
SampleSizeFactor: measures the statistical reliability of a country's fraud
rate estimate based on how many historical transactions back it - NOT the
fraud risk itself.

Design:
- Uses a logarithmic saturation curve: confidence grows quickly for small
  samples, then flattens as sample size increases, asymptotically
  approaching 1.0. This mirrors how statistical reliability actually behaves
  (diminishing returns from additional samples).
- The single calibration point is settings.sample_size_reference: the sample
  size at which the curve reaches ~90% confidence. Everything else derives
  from this one configurable anchor - no hardcoded breakpoints.
- score and confidence are set to the same value here: this factor's entire
  purpose IS to measure confidence, so its "risk score" is simply "how much
  can we trust the numbers", not a fraud signal. The CountryScoreEngine's
  confidence-weighted aggregation (effective_weight = weight * confidence)
  means a low-confidence SampleSizeFactor naturally contributes less to the
  final blended score, which is exactly the intended effect.
"""

import math

from .base_factor import CountryFactor
from .models import FactorResult
from app.config import settings

FACTOR_NAME = "SampleSizeFactor"

# The curve reaches this fraction of maximum confidence at sample_size_reference.
_TARGET_AT_REFERENCE = 0.9


def _reliability_curve(sample_size: int, reference: float) -> float:
    """
    Logarithmic saturation curve: reliability(0) = 0, reliability(reference) ≈
    _TARGET_AT_REFERENCE, reliability(inf) -> 1.0.

    Uses reliability(n) = 1 - (1 - target) ** (n / reference), which is smooth,
    monotonically increasing, and has exactly one configurable parameter.
    """
    if reference <= 0 or sample_size <= 0:
        return 0.0
    ratio = sample_size / reference
    reliability = 1.0 - (1.0 - _TARGET_AT_REFERENCE) ** ratio
    return max(0.0, min(1.0, reliability))


class SampleSizeFactor(CountryFactor):
    """Scores the statistical reliability of a country's data, independent of its risk level."""

    def score(self, transaction: dict, stats: dict) -> FactorResult:
        weight = settings.sample_size_factor_weight
        country = transaction.get("country")
        country_stats = stats.get("country_stats", {})

        if not country or country not in country_stats:
            return FactorResult(
                factor_name=FACTOR_NAME,
                score=0.0,
                weight=weight,
                weighted_score=0.0,
                details="No transaction history available for this country.",
                confidence=0.0,
            )

        sample_size = country_stats[country]["total"]
        reliability = _reliability_curve(sample_size, settings.sample_size_reference)
        score = reliability * 100.0

        if reliability >= 0.75:
            reliability_label = "high"
        elif reliability >= 0.4:
            reliability_label = "moderate"
        else:
            reliability_label = "limited"

        details = (
            f"Country statistics are based on {sample_size} historical transactions. "
            f"Statistical reliability is {reliability_label}."
        )

        return FactorResult(
            factor_name=FACTOR_NAME,
            score=round(score, 2),
            weight=weight,
            weighted_score=round(score * weight, 2),
            details=details,
            confidence=round(reliability, 2),
        )
