"""
Central registry of country risk factors.

To add a new factor in the future (e.g. VelocityFactor, MerchantFactor,
DeviceFactor...):

1. Implement the CountryFactor interface in a new module in this package.
2. Import it here and add one line to FactorRegistry.default().

No other file needs to change; CountryScoreEngine only ever depends on
FactorRegistry, never on concrete factor classes directly.
"""

from .base_factor import CountryFactor
from .country_rate_factor import CountryRateFactor
from .sample_size_factor import SampleSizeFactor
from .trend_factor import TrendFactor


class FactorRegistry:
    """Holds the list of active CountryFactor instances used by the scoring engine."""

    def __init__(self, factors: list[CountryFactor] | None = None):
        self._factors: list[CountryFactor] = factors or []

    def register(self, factor: CountryFactor) -> None:
        """Adds a factor to the registry."""
        self._factors.append(factor)

    def all(self) -> list[CountryFactor]:
        """Returns all currently registered factors."""
        return list(self._factors)

    @classmethod
    def default(cls) -> "FactorRegistry":
        """Builds the default, production registry."""
        registry = cls()
        registry.register(CountryRateFactor())
        registry.register(SampleSizeFactor())
        registry.register(TrendFactor())
        # Future: registry.register(VelocityFactor())
        # Future: registry.register(MerchantFactor())
        return registry
