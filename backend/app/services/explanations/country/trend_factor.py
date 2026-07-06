"""
TrendFactor: scores whether a country's fraud rate is trending up or down
recently, compared to its own historical baseline.

Design:
- Compares country_recent_stats (last settings.country_trend_window_days) to
  country_stats (all-time) for the same country. A rising recent rate
  relative to the historical baseline signals an emerging risk pattern; a
  falling one signals improvement or a past issue being resolved.
- Uses the same sigmoid shape as CountryRateFactor, but centered on 1.0
  (recent rate == historical rate -> score 50, i.e. "no trend"), with slope
  derived from country_recent_stats availability rather than a fixed
  constant - trends are inherently noisier with less recent data, so the
  curve is intentionally gentler than CountryRateFactor's, controlled by a
  single configurable weight rather than a magic slope constant.
- confidence depends on how many recent transactions back the recent rate:
  a country with zero or very few recent transactions gets low confidence
  and a neutral score, rather than a misleadingly sharp trend reading.
- If country_recent_stats reports rate=None (below
  settings.country_trend_min_samples), this factor abstains gracefully.
"""

import math

from .base_factor import CountryFactor
from .models import FactorResult
from app.config import settings

FACTOR_NAME = "TrendFactor"

# Trend ratio (recent_rate / historical_rate) at which the sigmoid reaches
# ~90/100 - i.e. "recent rate is meaningfully higher than historical" is
# defined relative to the historical rate itself, not a fixed percentage.
_TREND_RATIO_AT_HIGH_SCORE = 2.0
_SIGMOID_TARGET_AT_RATIO = 0.9

# Sample size (recent transactions) at which trend confidence is considered full.
CONFIDENCE_FULL_SAMPLE_SIZE = 50
CONFIDENCE_FLOOR = 0.2


def _trend_slope() -> float:
    """
    Derives the sigmoid slope k such that sigmoid(1 + (_TREND_RATIO_AT_HIGH_SCORE - 1))
    == _SIGMOID_TARGET_AT_RATIO, centered at ratio=1.0 (no change).
    """
    target = _SIGMOID_TARGET_AT_RATIO
    logit = math.log(target / (1 - target))
    distance = _TREND_RATIO_AT_HIGH_SCORE - 1.0
    return logit / distance if distance > 0 else 0.0


class TrendFactor(CountryFactor):
    """Scores whether a country's recent fraud rate is rising relative to its own history."""

    def score(self, transaction: dict, stats: dict) -> FactorResult:
        weight = settings.trend_factor_weight
        country = transaction.get("country")
        country_stats = stats.get("country_stats", {})
        recent_stats = stats.get("country_recent_stats", {})

        if not country or country not in country_stats:
            return FactorResult(
                factor_name=FACTOR_NAME,
                score=0.0,
                weight=weight,
                weighted_score=0.0,
                details="Insufficient historical data to assess trend.",
                confidence=0.0,
            )

        historical_rate = country_stats[country]["rate"]
        recent_entry = recent_stats.get(country)

        if not recent_entry or recent_entry.get("rate") is None:
            return FactorResult(
                factor_name=FACTOR_NAME,
                score=50.0,
                weight=weight,
                weighted_score=round(50.0 * 0.0, 2),
                details=(
                    f"Not enough recent transactions in the last "
                    f"{settings.country_trend_window_days} days to assess a trend."
                ),
                confidence=0.0,
            )

        recent_rate = recent_entry["rate"]
        recent_sample = recent_entry["total"]

        if historical_rate <= 0:
            trend_ratio = 1.0 if recent_rate <= 0 else 2.0
        else:
            trend_ratio = recent_rate / historical_rate

        slope = _trend_slope()
        if slope <= 0:
            score = 50.0
        else:
            try:
                score = 100.0 / (1.0 + math.exp(-slope * (trend_ratio - 1.0)))
            except OverflowError:
                score = 100.0 if trend_ratio > 1.0 else 0.0

        score = max(0.0, min(100.0, score))
        confidence = min(1.0, max(CONFIDENCE_FLOOR, recent_sample / CONFIDENCE_FULL_SAMPLE_SIZE))

        direction = "increasing" if trend_ratio > 1.05 else "decreasing" if trend_ratio < 0.95 else "stable"

        details = (
            f"Recent fraud rate ({recent_rate * 100:.2f}% over the last "
            f"{settings.country_trend_window_days} days, {recent_sample} transactions) is {direction} "
            f"compared to the historical rate ({historical_rate * 100:.2f}%)."
        )

        return FactorResult(
            factor_name=FACTOR_NAME,
            score=round(score, 2),
            weight=weight,
            weighted_score=round(score * weight, 2),
            details=details,
            confidence=round(confidence, 2),
        )
