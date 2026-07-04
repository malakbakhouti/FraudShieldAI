# FraudShield AI – Real-Time Bank Fraud Detection Platform

FraudShield AI is a full-stack banking fraud monitoring platform that detects fraudulent transactions in real time using a Machine Learning scoring engine, and provides fraud analysts with the tools to review, confirm, and manage alerts.

This project was developed as a personal portfolio project applied to the Master MIAGE IA2 (Intelligence Artificielle Appliquée) double-degree program.

Link: https://github.com/malakbakhouti/FraudShieldAI

## Problem & Approach

Banks process thousands to millions of transactions daily. Fraud is extremely rare (under 0.2% of transactions) but costly, while over-blocking legitimate transactions harms customer trust. FraudShield AI addresses this by scoring every transaction in real time with a Random Forest classifier, trained with SMOTE oversampling to handle the extreme class imbalance, and evaluated using ROC-AUC and PR-AUC rather than raw accuracy.

## Application Pages

| Page | Description |
|---|---|
| Login / Signup | JWT-based authentication |
| Dashboard | Live transaction feed, global stats, real-time chart |
| Transactions | Full transaction history with filters |
| Transaction Details | Customer info, AI prediction, fraud probability, top contributing model features |
| Alerts | Suspicious transactions requiring review — Mark as Legitimate, Confirm Fraud, Close Alert |
| Reports | Fraud evolution, transactions per day, detection performance, CSV export |
| Users *(Admin only)* | Create, edit, delete users and assign roles |
| Models *(Admin only)* | Deployed model info, comparison against alternative algorithms, feature importance |
| Settings | Profile, password change, alert threshold, notification preferences |

## User Roles

- **Admin** — full access, including User Management and Models
- **Fraud Analyst** — Dashboard, Transactions, Alerts, Reports, Settings (no user or model administration)

## Architecture Overview

| Component | Type | Role |
|---|---|---|
| Frontend | Angular | Authenticated dashboard, alerts workflow, reports, admin panels |
| Backend | FastAPI | JWT auth, REST API, WebSocket streaming, ML inference |
| Database | PostgreSQL | Users, transactions, roles |
| ML Layer | Scikit-learn | Offline model training, evaluation, serialization |

## ML Model

- **Algorithm**: Random Forest Classifier (200 estimators, max depth 12), selected after comparison against Logistic Regression and Decision Tree
- **Class balancing**: SMOTE oversampling
- **Evaluation**: Accuracy, Precision, Recall, F1, ROC-AUC, PR-AUC (imbalance-aware metrics)
- **Training data**: Credit Card Fraud Detection Dataset (Kaggle), 284,807 transactions, PCA-anonymized features (V1–V28)
- The model is trained offline during development; the deployed application performs inference only. Retraining is intentionally disabled from the UI.

## Key Workflow

```
Login → Dashboard → Transactions → AI Fraud Detection
  → Normal: transaction accepted
  → Suspicious: Alert created → Fraud Analyst reviews
      → Mark as Legitimate / Confirm Fraud → Close Alert
```

## Run the Project

**Backend**
```
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

**Frontend**
```
cd frontend
npm install
ng serve
```

**ML Model (training, offline only)**
```
cd ml
source venv/bin/activate
jupyter notebook fraud_detection_model.ipynb
```

Requires a local PostgreSQL database (`bank_fraud_db`) matching the connection string in `backend/app/config.py`.

## Future Improvements

- Kafka-based real streaming pipeline (replacing the simulated transaction feed)
- Deep learning model comparison (autoencoders for anomaly detection)
- SHAP-based explainability layer for flagged transactions
- Containerized deployment (Docker + cloud hosting)

## Conclusion

FraudShield AI demonstrates a complete, role-based banking fraud monitoring platform — from an offline-trained, comparison-justified ML model to a real-time detection pipeline and a full analyst workflow, rather than a standalone machine learning experiment.
