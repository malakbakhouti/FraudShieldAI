import asyncio
import json
import random

COUNTRY_WEIGHTS = {
    'France': 20, 'Germany': 15, 'United States': 15, 'United Kingdom': 12,
    'Spain': 8, 'Italy': 8, 'Morocco': 6, 'Brazil': 5, 'Russia': 4,
    'India': 4, 'Nigeria': 2, 'Indonesia': 1
}

def pick_country():
    countries = list(COUNTRY_WEIGHTS.keys())
    weights = list(COUNTRY_WEIGHTS.values())
    return random.choices(countries, weights=weights, k=1)[0]
import numpy as np
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.transaction import Transaction
from app.services.fraud_detector import fraud_detector

router = APIRouter()

def generate_fake_transaction() -> dict:
    """Simule une transaction (remplace par un vrai flux de données en prod)."""
    features = {f"V{i}": round(random.gauss(0, 1.5), 4) for i in range(1, 29)}
    features["Amount_scaled"] = round(random.gauss(0, 1), 4)
    features["Time_scaled"] = round(random.gauss(0, 1), 4)
    return features

@router.websocket("/ws/transactions")
async def transactions_stream(websocket: WebSocket):
    await websocket.accept()
    db: Session = SessionLocal()
    try:
        while True:
            features = generate_fake_transaction()
            result = fraud_detector.predict(features)
            amount = round(random.uniform(5, 3000), 2)

            tx = Transaction(
                amount=amount,
                features=json.dumps(features),
                fraud_probability=result["fraud_probability"],
                is_fraud=result["is_fraud"],
                country=pick_country()
            )
            db.add(tx)
            db.commit()
            db.refresh(tx)

            await websocket.send_json({
                "id": tx.id,
                "amount": tx.amount,
                "fraud_probability": tx.fraud_probability,
                "is_fraud": tx.is_fraud,
                "created_at": tx.created_at.isoformat()
            })
            await asyncio.sleep(1.5)
    except WebSocketDisconnect:
        pass
    finally:
        db.close()
