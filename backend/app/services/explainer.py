"""
ExplanationEngine: single entry point that orchestrates all explanation
sub-engines (Country, and future Transaction/Model/Merchant engines) and
returns one stable, extensible structure.

Design:
- This module never contains scoring logic itself. It only:
    1. Loads statistics from DataStatsProvider.
    2. Runs each registered sub-engine (currently CountryScoreEngine).
    3. Combines their scores into a single overall_risk score/severity.
    4. Flattens each sub-engine's factor results into a unified "reasons" list.
- Adding a new sub-engine (TransactionScoreEngine, ModelScoreEngine...) later
  means: run it here, add its named section to the response, and fold its
  factors into `reasons` - no other file needs to change, and no scoring
  logic is duplicated (each sub-engine owns its own factors/weights).
- The overall_risk score is a simple average of sub-engine scores for now;
  this is intentionally the only "combination" decision made at this layer,
  kept separate from how each sub-engine computes its own internal score.
"""

from sqlalchemy.orm import Session

from app.services.data_stats import get_data_stats
from app.services.explanations.country.country_score import CountryScoreEngine
from app.services.explanations.country.factor_registry import FactorRegistry

_country_engine = CountryScoreEngine(FactorRegistry.default())


def _severity_from_score(score: float) -> str:
    if score <= 39:
        return "low"
    if score <= 69:
        return "medium"
    return "high"


def _country_section(transaction: dict, stats: dict) -> dict:
    country_score = _country_engine.evaluate(transaction, stats)
    return {
        "score": country_score.final_score,
        "severity": country_score.severity,
        "factors": [
            {
                "factor_name": f.factor_name,
                "score": f.score,
                "weight": f.weight,
                "weighted_score": f.weighted_score,
                "confidence": f.confidence,
                "details": f.details,
            }
            for f in country_score.factors
        ],
        "details": country_score.details,
    }


def _reasons_from_country_section(country_section: dict) -> list[dict]:
    """
    Maps a sub-engine's factor results into the flattened, human-facing
    `reasons` list. Each sub-engine is responsible for producing factors with
    a `details` string; this function only handles presentation (titling),
    never scoring.
    """
    title_map = {
        "CountryRateFactor": "High Risk Country",
        "SampleSizeFactor": "Statistical Reliability",
        "TrendFactor": "Fraud Trend",
    }

    reasons = []
    for factor in country_section["factors"]:
        title = title_map.get(factor["factor_name"], factor["factor_name"])
        reasons.append({
            "title": title,
            "severity": _severity_from_score(factor["score"]),
            "score": factor["score"],
            "details": factor["details"],
        })
    return reasons


def generate_explanation(transaction: dict, db: Session) -> dict:
    """
    Public entry point. Given a transaction dict (amount, country, features,
    fraud_probability) and a DB session, returns the full explanation
    structure combining all sub-engines.

    Args:
        transaction: dict with at least amount, country, features, fraud_probability.
        db: active SQLAlchemy session, used to fetch cached DataStatsProvider stats.

    Returns:
        {
            "overall_risk": {"score": float, "severity": str},
            "country": {"score": float, "severity": str, "factors": [...], "details": [...]},
            "reasons": [{"title": str, "severity": str, "score": float, "details": str}, ...]
        }
    """
    stats = get_data_stats(db)

    country_section = _country_section(transaction, stats)

    # Only one sub-engine exists today; overall_risk mirrors it directly.
    # Future sub-engines get added to this list and averaged together.
    sub_engine_scores = [country_section["score"]]
    overall_score = sum(sub_engine_scores) / len(sub_engine_scores)
    overall_severity = _severity_from_score(overall_score)

    reasons = _reasons_from_country_section(country_section)
    reasons.sort(key=lambda r: {"high": 0, "medium": 1, "low": 2, "info": 3}.get(r["severity"], 99))

    return {
        "overall_risk": {
            "score": round(overall_score, 2),
            "severity": overall_severity,
        },
        "country": country_section,
        "reasons": reasons,
    }
