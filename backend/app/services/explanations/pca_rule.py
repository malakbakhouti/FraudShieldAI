from .base_rule import Explanation

# A feature value is "anomalous" if it deviates from the dataset mean by more
# than this many standard deviations (a standard statistical outlier threshold,
# not a fixed magic number tied to any specific feature).
Z_SCORE_THRESHOLD = 3.0
MULTI_FEATURE_THRESHOLD = 3


class PcaRule:
    """Flags transactions with statistically abnormal PCA feature values (V1-V28)."""

    def evaluate(self, transaction: dict, stats: dict) -> list[Explanation]:
        features = transaction.get("features", {})
        feature_stats = stats.get("feature_stats", {})

        if not features or not feature_stats:
            return []

        anomalous_count = 0
        for key, value in features.items():
            if key not in feature_stats:
                continue
            mean = feature_stats[key]["mean"]
            stdev = feature_stats[key]["stdev"] or 1.0
            z_score = abs((value - mean) / stdev)
            if z_score > Z_SCORE_THRESHOLD:
                anomalous_count += 1

        if anomalous_count >= MULTI_FEATURE_THRESHOLD:
            return [Explanation(reason="Multiple Anomalous Behaviour Patterns Detected", severity="high")]
        if anomalous_count >= 1:
            return [Explanation(reason="Unusual Feature Distribution", severity="low")]

        return []
