from sqlalchemy import Column, Integer, Float, String, DateTime, Boolean
from sqlalchemy.sql import func
from app.database import Base

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float, nullable=False)
    features = Column(String, nullable=False)  # JSON stringifié des V1-V28
    fraud_probability = Column(Float, nullable=False)
    is_fraud = Column(Boolean, default=False, index=True)
    country = Column(String, default='Unknown')
    created_at = Column(DateTime(timezone=True), server_default=func.now())
