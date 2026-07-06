from .base_rule import Explanation
from app.config import settings


class CountryRule:
    """
    Flags transactions from countries whose fraud rate significantly exceeds
    the global average. Two severity tiers, both driven by configurable
    multipliers (app/config.py), not fixed thresholds:

    - Medium Risk Country: rate >= global_rate * country_risk_medium_multiplier
    - High Risk Country:   rate >= global_rate * country_risk_high_multiplier

    Countries with fewer than MIN_SAMPLES_FOR_COUNTRY_RATE transactions are
    excluded upstream by DataStatsProvider, so this rule never fires on
    statistically unreliable samples.
    """

    def evaluate(self, transaction: dict, stats: dict) -> list[Explanation]:
        country = transaction.get("country")
        country_rates = stats.get("country_fraud_rates", {})
        global_rate = stats.get("global_fraud_rate", 0)

        if not country or country not in country_rates or global_rate <= 0:
            return []

        country_rate = country_rates[country]

        if country_rate >= global_rate * settings.country_risk_high_multiplier:
            return [Explanation(reason="High Risk Country", severity="high")]

        if country_rate >= global_rate * settings.country_risk_medium_multiplier:
            return [Explanation(reason="Medium Risk Country", severity="medium")]

        return []
