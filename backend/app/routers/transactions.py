from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from app.database import get_db
from app.models.transaction import Transaction
from app.schemas.transaction import TransactionOut, TransactionStats

router = APIRouter(prefix="/api/transactions", tags=["transactions"])

@router.get("/", response_model=List[TransactionOut])
def get_transactions(limit: int = 50, db: Session = Depends(get_db)):
    return db.query(Transaction).order_by(Transaction.created_at.desc()).limit(limit).all()

@router.get("/stats", response_model=TransactionStats)
def get_stats(db: Session = Depends(get_db)):
    total = db.query(func.count(Transaction.id)).scalar() or 0
    frauds = db.query(func.count(Transaction.id)).filter(Transaction.is_fraud == True).scalar() or 0
    avg_amount = db.query(func.avg(Transaction.amount)).scalar() or 0.0
    return TransactionStats(
        total_transactions=total,
        total_frauds=frauds,
        fraud_rate=(frauds / total * 100) if total else 0.0,
        avg_amount=round(avg_amount, 2)
    )
