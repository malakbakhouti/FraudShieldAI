from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from app.database import get_db
from app.models.transaction import Transaction
from app.schemas.transaction import TransactionOut, TransactionStats
from fastapi import HTTPException
import json

router = APIRouter(prefix="/api/transactions", tags=["transactions"])

@router.get("/", response_model=List[TransactionOut])
def get_transactions(limit: int = 50, db: Session = Depends(get_db)):
    return db.query(Transaction).order_by(Transaction.created_at.desc()).limit(limit).all()


@router.get("/daily-summary")
def get_daily_summary(db: Session = Depends(get_db)):
    from sqlalchemy import cast, Date
    results = (
        db.query(
            cast(Transaction.created_at, Date).label("day"),
            func.count(Transaction.id).filter(Transaction.is_fraud == True).label("frauds"),
            func.count(Transaction.id).label("total")
        )
        .group_by(cast(Transaction.created_at, Date))
        .order_by(cast(Transaction.created_at, Date))
        .all()
    )
    return [
        {"day": r.day.strftime("%d %b"), "frauds": r.frauds, "total": r.total}
        for r in results
    ]


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


@router.get("/{transaction_id}")
def get_transaction_detail(transaction_id: int, db: Session = Depends(get_db)):
    from app.services.explainer import generate_explanation

    tx = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")

    try:
        features = json.loads(tx.features)
    except Exception:
        features = {}

    transaction_payload = {
        "amount": tx.amount,
        "country": tx.country,
        "fraud_probability": tx.fraud_probability,
        "features": features,
    }

    try:
        explanation = generate_explanation(transaction_payload, db)
    except Exception:
        explanation = None

    return {
        "id": tx.id,
        "amount": tx.amount,
        "country": tx.country,
        "fraud_probability": tx.fraud_probability,
        "is_fraud": tx.is_fraud,
        "created_at": tx.created_at,
        "features": features,
        "explanation": explanation
    }

@router.get("/analytics/top-countries")
def get_top_countries(db: Session = Depends(get_db)):
    results = (
        db.query(
            Transaction.country,
            func.count(Transaction.id).filter(Transaction.is_fraud == True).label("frauds")
        )
        .filter(Transaction.country != None, Transaction.country != "Unknown")
        .group_by(Transaction.country)
        .order_by(func.count(Transaction.id).filter(Transaction.is_fraud == True).desc())
        .limit(5)
        .all()
    )
    return [{"name": r.country, "value": r.frauds} for r in results if r.frauds > 0]


@router.get("/analytics/risk-distribution")
def get_risk_distribution(db: Session = Depends(get_db)):
    total = db.query(func.count(Transaction.id)).scalar() or 1

    high = db.query(func.count(Transaction.id)).filter(Transaction.fraud_probability >= 0.7).scalar() or 0
    medium = db.query(func.count(Transaction.id)).filter(
        Transaction.fraud_probability >= 0.3, Transaction.fraud_probability < 0.7
    ).scalar() or 0
    low = db.query(func.count(Transaction.id)).filter(Transaction.fraud_probability < 0.3).scalar() or 0

    return {
        "high": round(high / total * 100, 1),
        "medium": round(medium / total * 100, 1),
        "low": round(low / total * 100, 1)
    }
