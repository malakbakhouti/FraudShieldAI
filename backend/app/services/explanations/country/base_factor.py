"""
Abstract base class that every country risk factor must implement.

Each concrete factor (CountryRateFactor, TrendFactor, SampleFactor,
ConfidenceFactor, and future ones) evaluates one specific dimension of risk
for a given transaction and returns a FactorResult. Factors are intentionally
independent of one another: the engine is responsible for combining them,
never a factor itself.
"""

from abc import ABC, abstractmethod
from .models import FactorResult


class CountryFactor(ABC):
    """
    Contract for a single country risk factor.

    Implementations must be side-effect free and must not raise on missing
    or incomplete data; instead they should return a FactorResult with a low
    score and confidence, or raise only for truly unexpected programming
    errors (the engine will catch and log any exception regardless, but
    well-behaved factors should not rely on that as their normal control flow).
    """

    @abstractmethod
    def score(self, transaction: dict, stats: dict) -> FactorResult:
        """
        Evaluates this factor for the given transaction.

        Args:
            transaction: dict with at least amount, country, features,
                fraud_probability.
            stats: the dict returned by data_stats.get_data_stats(), containing
                country_stats, country_recent_stats, global_fraud_rate, etc.

        Returns:
            A FactorResult describing this factor's contribution.
        """
        raise NotImplementedError
