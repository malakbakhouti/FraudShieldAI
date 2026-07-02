from pydantic import BaseModel
from datetime import datetime

class TransactionOut(BaseModel):
    id: int
    amount: float
    fraud_probability: float
    is_fraud: bool
    created_at: datetime

    class Config:
        from_attributes = True

class TransactionStats(BaseModel):
    total_transactions: int
    total_frauds: int
    fraud_rate: float
    avg_amount: float
