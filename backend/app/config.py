import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql://malak@localhost:5432/bank_fraud_db"
    )
    model_path: str = os.getenv("MODEL_PATH", "app/models/fraud_model.joblib")
    scaler_path: str = os.getenv("SCALER_PATH", "app/models/scaler.joblib")
    features_path: str = os.getenv("FEATURES_PATH", "app/models/feature_columns.joblib")
    stats_cache_ttl_seconds: int = int(os.getenv("STATS_CACHE_TTL_SECONDS", "60"))
    country_risk_medium_multiplier: float = float(os.getenv("COUNTRY_RISK_MEDIUM_MULTIPLIER", "3.0"))
    country_risk_high_multiplier: float = float(os.getenv("COUNTRY_RISK_HIGH_MULTIPLIER", "5.0"))
    country_trend_window_days: int = int(os.getenv("COUNTRY_TREND_WINDOW_DAYS", "7"))
    country_trend_min_samples: int = int(os.getenv("COUNTRY_TREND_MIN_SAMPLES", "10"))
    country_rate_factor_weight: float = float(os.getenv("COUNTRY_RATE_FACTOR_WEIGHT", "0.40"))
    sample_size_factor_weight: float = float(os.getenv("SAMPLE_SIZE_FACTOR_WEIGHT", "0.20"))
    sample_size_reference: float = float(os.getenv("SAMPLE_SIZE_REFERENCE", "200"))
    trend_factor_weight: float = float(os.getenv("TREND_FACTOR_WEIGHT", "0.20"))

settings = Settings()
