import joblib
import numpy as np
from app.config import settings

class FraudDetector:
    def __init__(self):
        self.model = joblib.load(settings.model_path)
        self.scaler = joblib.load(settings.scaler_path)
        self.feature_columns = joblib.load(settings.features_path)

    def predict(self, features: dict) -> dict:
        row = [features.get(col, 0.0) for col in self.feature_columns]
        X = np.array(row).reshape(1, -1)
        proba = self.model.predict_proba(X)[0][1]
        return {
            "fraud_probability": float(proba),
            "is_fraud": bool(proba >= 0.5)
        }

fraud_detector = FraudDetector()
