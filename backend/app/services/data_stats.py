"""
DataStatsProvider

Computes and caches real statistical parameters derived from stored transactions,
used by the Explanation Service (app/services/explainer.py) and the Country Risk
Scoring Engine (app/services/explanations/country/) to generate dynamic,
data-driven fraud explanations.

Design:
- Each statistic is computed by an independent "stat provider" function.
- Providers are registered in STAT_PROVIDERS and run independently; a failure in
  one provider never breaks the others (each is wrapped in its own try/except
  and logged, then falls back to a safe default).
- To add a new statistic (e.g. merchant fraud rate, hourly fraud rate, velocity),
  write a new `_compute_xxx(db)` function returning a picklable value, then add
  it to STAT_PROVIDERS with its default fallback value. No other code changes needed.
- Metadata (last_refresh, cache_ttl, sample_size, computation_duration_ms) is
  exposed alongside the stats for monitoring and debugging.
- Call invalidate_cache() after a dataset import so the Explanation Service
  immediately uses fresh statistics instead of waiting for TTL expiry.
"""

import json
import logging
import statistics
import time
from datetime import datetime, timedelta
from typing import Callable, Any
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.models.transaction import Transaction
from app.config import settings

logger = logging.getLogger("data_stats")

_CACHE: dict[str, Any] = {"stats": None, "computed_at": 0.0, "meta": None}

MIN_SAMPLES_FOR_COUNTRY_RATE = 30
MIN_SAMPLES_FOR_FEATURE_STATS = 10
FEATURE_SAMPLE_LIMIT = 3000

DEFAULT_STATS = {
    "amount_p95": 1000.0,
    "global_fraud_rate": 0.0,
    "country_fraud_rates": {},
    "country_stats": {},
    "country_recent_stats": {},
    "country_ratio_distribution": {"median": 1.0, "spread": 1.0, "sample_countries": 0},
    "feature_stats": {},
}


def _compute_amount_p95(db: Session) -> float:
    row = db.query(
        func.percentile_cont(0.95).within_group(Transaction.amount.asc())
    ).scalar()
    return float(row) if row is not None else DEFAULT_STATS["amount_p95"]


def _compute_global_fraud_rate(db: Session) -> float:
    total = db.query(func.count(Transaction.id)).scalar() or 0
    if total == 0:
        return DEFAULT_STATS["global_fraud_rate"]
    frauds = db.query(func.count(Transaction.id)).filter(Transaction.is_fraud == True).scalar() or 0
    return frauds / total


def _compute_country_stats(db: Session) -> dict[str, dict]:
    """
    Returns per-country {total, frauds, rate} for countries with enough
    samples to be statistically meaningful (>= MIN_SAMPLES_FOR_COUNTRY_RATE).

    This is the richer, canonical source of country-level data. Used directly
    by the Country Risk Scoring Engine, and also backs the legacy
    country_fraud_rates stat below for backward compatibility.
    """
    rows = (
        db.query(
            Transaction.country,
            func.count(Transaction.id).label("total"),
            func.count(Transaction.id).filter(Transaction.is_fraud == True).label("frauds")
        )
        .filter(Transaction.country.isnot(None), Transaction.country != "Unknown")
        .group_by(Transaction.country)
        .all()
    )

    result = {}
    for r in rows:
        if not r.country or not r.total or r.total < MIN_SAMPLES_FOR_COUNTRY_RATE:
            continue
        result[r.country] = {
            "total": r.total,
            "frauds": r.frauds,
            "rate": r.frauds / r.total,
        }
    return result


def _compute_country_fraud_rates(db: Session) -> dict[str, float]:
    """
    Backward-compatible view of _compute_country_stats: {country: rate}.
    Kept so existing consumers of `stats["country_fraud_rates"]` (e.g. the
    original CountryRule, dashboards) keep working unchanged.
    """
    country_stats = _compute_country_stats(db)
    return {country: data["rate"] for country, data in country_stats.items()}


def _compute_country_recent_stats(db: Session) -> dict[str, dict]:
    """
    Same shape as _compute_country_stats, but restricted to a recent time
    window (settings.country_trend_window_days). Used by the Country Risk
    Scoring Engine's trend factor to detect whether a country's fraud rate is
    rising or falling compared to its historical baseline.

    A country with fewer than settings.country_trend_min_samples recent
    transactions gets rate=None, signalling "not enough recent data" rather
    than a false 0% or misleading rate.
    """
    cutoff = datetime.utcnow() - timedelta(days=settings.country_trend_window_days)

    rows = (
        db.query(
            Transaction.country,
            func.count(Transaction.id).label("total"),
            func.count(Transaction.id).filter(Transaction.is_fraud == True).label("frauds")
        )
        .filter(
            Transaction.country.isnot(None),
            Transaction.country != "Unknown",
            Transaction.created_at >= cutoff,
        )
        .group_by(Transaction.country)
        .all()
    )

    result = {}
    for r in rows:
        total = r.total or 0
        frauds = r.frauds or 0

        if total < settings.country_trend_min_samples:
            result[r.country] = {"total": total, "frauds": frauds, "rate": None}
            continue

        result[r.country] = {
            "total": total,
            "frauds": frauds,
            "rate": frauds / total,
        }
    return result


def _compute_country_ratio_distribution(db: Session) -> dict:
    """
    Computes the real distribution of (country_rate / global_rate) ratios
    across all countries with sufficient samples, used to dynamically
    calibrate the CountryRateFactor's sigmoid scoring function.

    Returns:
        median: the median ratio across countries. Used as the sigmoid's
            center (score = 50 at this ratio), so "average risk relative to
            peers" always maps to the midpoint regardless of how the overall
            fraud landscape shifts over time.
        spread: the interquartile range (P75 - P25) of ratios. Used to derive
            the sigmoid's slope, so the scoring curve stretches or compresses
            automatically to match how spread out the real data currently is.
            Falls back to the standard deviation, then to a small numerical
            safety floor, if there isn't enough variation to compute an IQR
            (e.g. very few countries, or all countries near-identical).
        sample_countries: how many countries contributed to this distribution,
            exposed so consumers can judge how reliable median/spread are.
    """
    country_stats = _compute_country_stats(db)
    global_rate = _compute_global_fraud_rate(db)

    if not country_stats or global_rate <= 0:
        return dict(DEFAULT_STATS["country_ratio_distribution"])

    ratios = sorted(
        data["rate"] / global_rate
        for data in country_stats.values()
        if global_rate > 0
    )

    if not ratios:
        return dict(DEFAULT_STATS["country_ratio_distribution"])

    median = statistics.median(ratios)

    spread: float
    if len(ratios) >= 4:
        try:
            quantiles = statistics.quantiles(ratios, n=4)
            spread = quantiles[2] - quantiles[0]  # P75 - P25
        except statistics.StatisticsError:
            spread = 0.0
    else:
        spread = 0.0

    if spread <= 0 and len(ratios) > 1:
        try:
            spread = statistics.stdev(ratios)
        except statistics.StatisticsError:
            spread = 0.0

    if spread <= 0:
        # Degenerate case (single country, or all ratios identical): fall back
        # to a small fraction of the median itself, so the sigmoid still has a
        # sensible, non-zero slope instead of becoming a step function.
        spread = max(median * 0.25, 0.01)

    return {
        "median": median,
        "spread": spread,
        "sample_countries": len(ratios),
    }


def _compute_feature_stats(db: Session) -> dict[str, dict[str, float]]:
    rows = (
        db.query(Transaction.features)
        .order_by(Transaction.id.desc())
        .limit(FEATURE_SAMPLE_LIMIT)
        .all()
    )

    feature_values: dict[str, list[float]] = {}
    skipped_rows = 0

    for row in rows:
        if not row.features:
            continue
        try:
            parsed = json.loads(row.features)
        except (json.JSONDecodeError, TypeError):
            skipped_rows += 1
            continue
        if not isinstance(parsed, dict):
            skipped_rows += 1
            continue
        for key, val in parsed.items():
            if not isinstance(key, str) or not key.startswith("V"):
                continue
            try:
                feature_values.setdefault(key, []).append(float(val))
            except (TypeError, ValueError):
                continue

    if skipped_rows > 0:
        logger.warning(f"[data_stats] Skipped {skipped_rows} rows with corrupted/invalid features JSON")

    result = {}
    for key, values in feature_values.items():
        if len(values) < MIN_SAMPLES_FOR_FEATURE_STATS:
            continue
        try:
            result[key] = {
                "mean": statistics.mean(values),
                "stdev": statistics.stdev(values) if len(values) > 1 else 1.0,
            }
        except statistics.StatisticsError as e:
            logger.warning(f"[data_stats] Could not compute stats for feature {key}: {e}")
            continue
    return result


# Registry of stat providers: name -> (compute_fn, default_fallback_value)
# Add new entries here to extend the provider without touching the rest of the code.
STAT_PROVIDERS: dict[str, tuple[Callable[[Session], Any], Any]] = {
    "amount_p95": (_compute_amount_p95, DEFAULT_STATS["amount_p95"]),
    "global_fraud_rate": (_compute_global_fraud_rate, DEFAULT_STATS["global_fraud_rate"]),
    "country_fraud_rates": (_compute_country_fraud_rates, DEFAULT_STATS["country_fraud_rates"]),
    "country_stats": (_compute_country_stats, DEFAULT_STATS["country_stats"]),
    "country_recent_stats": (_compute_country_recent_stats, DEFAULT_STATS["country_recent_stats"]),
    "country_ratio_distribution": (_compute_country_ratio_distribution, DEFAULT_STATS["country_ratio_distribution"]),
    "feature_stats": (_compute_feature_stats, DEFAULT_STATS["feature_stats"]),
}


def invalidate_cache() -> None:
    """
    Forces the next call to get_data_stats() to recompute statistics from scratch,
    ignoring the TTL. Call this after importing a new dataset so the Explanation
    Service immediately reflects the latest data.
    """
    _CACHE["stats"] = None
    _CACHE["computed_at"] = 0.0
    _CACHE["meta"] = None
    logger.info("[data_stats] Cache invalidated manually")


def refresh_data_stats(db: Session) -> dict:
    """Convenience wrapper: invalidate the cache and recompute immediately."""
    invalidate_cache()
    return get_data_stats(db, force_refresh=True)


def get_data_stats(db: Session, force_refresh: bool = False) -> dict:
    now = time.time()
    ttl = settings.stats_cache_ttl_seconds

    if not force_refresh and _CACHE["stats"] is not None and (now - _CACHE["computed_at"] < ttl):
        return _CACHE["stats"]

    start = time.perf_counter()
    stats: dict[str, Any] = {}
    sample_size = db.query(func.count(Transaction.id)).scalar() or 0

    for name, (compute_fn, fallback) in STAT_PROVIDERS.items():
        try:
            stats[name] = compute_fn(db)
        except Exception as e:
            logger.error(f"[data_stats] Provider '{name}' failed, using fallback. Error: {e}", exc_info=True)
            stats[name] = fallback

    duration_ms = (time.perf_counter() - start) * 1000

    _CACHE["stats"] = stats
    _CACHE["computed_at"] = now
    _CACHE["meta"] = {
        "last_refresh": now,
        "cache_ttl": ttl,
        "sample_size": sample_size,
        "computation_duration_ms": round(duration_ms, 2),
    }

    logger.info(
        f"[data_stats] Refreshed stats cache in {duration_ms:.2f}ms "
        f"(sample_size={sample_size}): "
        f"amount_p95={stats['amount_p95']:.2f}, "
        f"global_fraud_rate={stats['global_fraud_rate']:.4f}, "
        f"countries_tracked={len(stats['country_stats'])}, "
        f"features_tracked={len(stats['feature_stats'])}"
    )

    return stats


def get_stats_metadata() -> dict | None:
    """
    Returns metadata about the last statistics computation, or None if
    statistics have never been computed yet.
    """
    return _CACHE["meta"]
