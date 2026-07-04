import pandas as pd
import numpy as np
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db, SessionLocal
from app.models.transaction import Transaction
from app.services.fraud_detector import fraud_detector
import json

router = APIRouter(prefix="/api/import", tags=["import"])

REQUIRED_COLUMNS = {"Time", "Amount"}


@router.post("/csv")
async def import_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="File must be a .csv")

    try:
        df = pd.read_csv(file.file)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not parse CSV: {e}")

    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise HTTPException(
            status_code=400,
            detail=f"CSV is missing required columns: {', '.join(missing)}"
        )

    scaler = fraud_detector.scaler
    feature_columns = fraud_detector.feature_columns

    total = 0
    fraud_count = 0
    errors = 0

    for _, row in df.iterrows():
        try:
            amount = float(row["Amount"])
            time_val = float(row["Time"])

            amount_scaled = float(scaler.transform([[amount]])[0][0])
            time_scaled = float(scaler.transform([[time_val]])[0][0])

            features = {}
            for col in feature_columns:
                if col == "Amount_scaled":
                    features[col] = amount_scaled
                elif col == "Time_scaled":
                    features[col] = time_scaled
                elif col in row and pd.notna(row[col]):
                    features[col] = float(row[col])
                else:
                    features[col] = 0.0

            result = fraud_detector.predict(features)

            tx = Transaction(
                amount=amount,
                features=json.dumps(features),
                fraud_probability=result["fraud_probability"],
                is_fraud=result["is_fraud"]
            )
            db.add(tx)
            total += 1
            if result["is_fraud"]:
                fraud_count += 1

        except Exception:
            errors += 1
            continue

    db.commit()

    return {
        "total_imported": total,
        "frauds_detected": fraud_count,
        "errors": errors,
        "fraud_rate": round((fraud_count / total * 100), 2) if total else 0
    }
