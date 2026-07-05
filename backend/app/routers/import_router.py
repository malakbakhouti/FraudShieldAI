import pandas as pd
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
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.models.transaction import Transaction
from app.models.import_log import ImportLog
from app.models.user import User
from app.services.fraud_detector import fraud_detector
from app.services.deps import get_current_user

router = APIRouter(prefix="/api/import", tags=["import"])

REQUIRED_COLUMNS = {"Time", "Amount"}


class ImportLogOut(BaseModel):
    id: int
    filename: str
    imported_by_email: str
    total_records: int
    frauds_detected: int
    errors: int
    status: str
    created_at: str

    class Config:
        from_attributes = True


@router.post("/preview")
async def preview_csv(file: UploadFile = File(...)):
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
            detail=f"Missing required columns: {', '.join(missing)}"
        )

    preview_rows = df.head(10).fillna("").to_dict(orient="records")

    return {
        "columns": list(df.columns),
        "total_rows": len(df),
        "preview": preview_rows
    }


@router.post("/csv")
async def import_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
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
    error_count = 0

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
                is_fraud=result["is_fraud"],
                country=pick_country()
            )
            db.add(tx)
            total += 1
            if result["is_fraud"]:
                fraud_count += 1

        except Exception:
            error_count += 1
            continue

    db.commit()

    log = ImportLog(
        filename=file.filename,
        imported_by_email=user.email,
        total_records=total,
        frauds_detected=fraud_count,
        errors=error_count,
        status="completed" if total > 0 else "failed"
    )
    db.add(log)
    db.commit()

    return {
        "total_imported": total,
        "frauds_detected": fraud_count,
        "errors": error_count,
        "fraud_rate": round((fraud_count / total * 100), 2) if total else 0
    }


@router.get("/history", response_model=list[ImportLogOut])
def get_import_history(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    logs = db.query(ImportLog).order_by(ImportLog.created_at.desc()).limit(50).all()
    return [
        ImportLogOut(
            id=l.id,
            filename=l.filename,
            imported_by_email=l.imported_by_email,
            total_records=l.total_records,
            frauds_detected=l.frauds_detected,
            errors=l.errors,
            status=l.status,
            created_at=l.created_at.isoformat()
        )
        for l in logs
    ]
