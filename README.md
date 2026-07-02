**FraudShield AI – Real‑Time Bank Fraud Detection**

FraudShield AI is a full‑stack system that detects fraudulent banking transactions in real time by combining a Machine Learning scoring engine with a live streaming architecture.
This project was developed as a personal portfolio project applied to the Master MIAGE IA2 (Intelligence Artificielle Appliquée) double‑degree program.

**🚀 Main Features**

**📊 Dashboard**
* Live transaction feed via WebSocket
* Fraud alerts highlighted in real time
* Global statistics (total transactions, fraud rate, average amount)

**🧠 Fraud Detection Engine**
* Real‑time scoring of every incoming transaction
* Probability‑based fraud classification (threshold 0.5)
* Model trained on highly imbalanced data (0.17% fraud rate)

**🗄️ Transaction History**
* Persisted transaction log with fraud scores
* REST endpoints for historical queries and stats

**🏗️ Architecture Overview**

FraudShield AI is split into 3 main components, each with a specific responsibility:

Component | Type | Role
---|---|---
Frontend | Angular | Real‑time dashboard, charts, alerts
Backend | FastAPI | WebSocket streaming, REST API, ML inference
ML Layer | Scikit-learn | Model training, evaluation, serialization

**🗄️ Components – Usage Summary**

**Frontend (Angular)**
* WebSocket client for live transaction stream
* Chart.js visualizations (transaction volume, fraud rate)
* 📁 frontend/src/app

**Backend (FastAPI)**
* /ws/transactions → WebSocket endpoint streaming scored transactions
* /api/transactions → REST endpoint for transaction history
* /api/transactions/stats → REST endpoint for aggregate statistics
* 📁 backend/app/routers, backend/app/services

**ML Layer (Scikit-learn)**
* Random Forest classifier (class_weight='balanced', 200 estimators)
* SMOTE oversampling to handle class imbalance
* Evaluation via ROC-AUC and PR-AUC (adapted to imbalanced data)
* 📁 ml/fraud_detection_model.ipynb

**🔄 Key Usage Scenario**

**1️⃣ Real‑time transaction scoring**
1. A transaction is generated (simulated stream) → Backend
2. Features are scaled and passed to the trained model → ML service
3. Fraud probability is computed → Backend
4. Transaction + score is persisted → PostgreSQL
5. Result is pushed to the client → WebSocket
6. Dashboard updates instantly → Frontend

**▶️ Run the Project**

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

**ML Model**
```
cd ml
source venv/bin/activate
jupyter notebook fraud_detection_model.ipynb
```

**🔮 Future Improvements**
* Kafka-based real streaming pipeline (replacing simulated transactions)
* Deep learning model comparison (autoencoders for anomaly detection)
* Explainability layer (SHAP) for flagged transactions
* Deployment (Docker + cloud hosting)

**🎤 Conclusion**

FraudShield AI demonstrates an end‑to‑end ML system applied to a real‑world problem: combining a trained classifier, a real‑time API layer, and a live dashboard to detect fraud as transactions happen, rather than after the fact.
