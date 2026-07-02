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

settings = Settings()
