**FraudShield AI – Real‑Time Bank Fraud Detection Platform**

FraudShield AI is a full‑stack banking fraud monitoring platform that detects fraudulent transactions in real time by combining a Machine Learning scoring engine with a real‑time detection pipeline, and gives fraud analysts the tools to review, confirm, and manage alerts.

This project was developed as a personal portfolio project applied to the Master MIAGE IA2 (Intelligence Artificielle Appliquée) double‑degree program.

**🚀 Main Features**

**📊 Dashboard**
* Live transaction feed via WebSocket
* Fraud alerts highlighted in real time
* Global statistics (total transactions, fraud rate, average amount)

**🧠 Fraud Detection Engine**
* Real‑time scoring of every incoming transaction
* Probability‑based fraud classification with a configurable decision threshold
* Model trained on highly imbalanced data (0.17% fraud rate)

**🔍 Transaction Details**
* Customer and transaction information
* AI prediction, fraud probability and risk level
* Top contributing model features (PCA components)

**🚨 Alerts Workflow**
* Suspicious transactions flagged for review
* Mark as Legitimate, Confirm Fraud, or Close Alert
* Full review lifecycle for fraud analysts

**📈 Reports**
* Transactions per day and fraud evolution
* Detection performance summary
* CSV export

**👥 User Management** *(Admin only)*
* Create, edit, and delete users
* Assign roles (Admin / Fraud Analyst)

**🧬 Models** *(Admin only)*
* Deployed model information and metrics
* Comparison against alternative algorithms
* Feature importance and training pipeline overview

**⚙️ Settings**
* Profile and password management
* Alert threshold configuration
* Notification preferences

**🔐 Authentication & Roles**
* JWT-based authentication
* Two roles: Admin (full access) and Fraud Analyst (Dashboard, Transactions, Alerts, Reports, Settings)

**🏗️ Architecture Overview**

FraudShield AI is split into 4 main components, each with a specific responsibility:

Component | Type | Role
---|---|---
Frontend | Angular | Authenticated dashboard, alerts workflow, reports, admin panels
Backend | FastAPI | JWT auth, REST API, WebSocket streaming, ML inference
Database | PostgreSQL | Users, transactions, roles
ML Layer | Scikit-learn | Offline model training, evaluation, serialization

**🗄️ Components – Usage Summary**

**Frontend (Angular)**
* WebSocket client for live transaction stream
* Alerts review workflow, reports charts, admin panels
* 📁 frontend/src/app

**Backend (FastAPI)**
* /api/auth → signup, login (JWT)
* /api/users → user management (Admin only)
* /ws/transactions → WebSocket endpoint streaming scored transactions
* /api/transactions → REST endpoint for transaction history and detail
* /api/transactions/stats → REST endpoint for aggregate statistics
* /api/settings → password change
* 📁 backend/app/routers, backend/app/services

**ML Layer (Scikit-learn)**
* Random Forest classifier selected after comparison against Logistic Regression and Decision Tree
* SMOTE oversampling to handle class imbalance
* Evaluation via ROC-AUC and PR-AUC (adapted to imbalanced data)
* 📁 ml/fraud_detection_model.ipynb

**🔄 Key Usage Scenario**

**1️⃣ Real‑time transaction scoring & review**
1. A transaction is generated (simulated real-time stream) → Backend
2. Features are scaled and passed to the trained model → ML service
3. Fraud probability is computed → Backend
4. Transaction + score is persisted → PostgreSQL
5. Result is pushed to the client → WebSocket
6. Dashboard updates instantly → Frontend
7. If suspicious, an Alert is created → Fraud Analyst reviews it
8. Analyst marks it as Legitimate or Confirms Fraud, then closes the alert

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

**ML Model** *(offline training only)*
```
cd ml
source venv/bin/activate
jupyter notebook fraud_detection_model.ipynb
```

Requires a local PostgreSQL database (`bank_fraud_db`) matching the connection string in `backend/app/config.py`.

**🔮 Future Improvements**
* Kafka-based real streaming pipeline (replacing the simulated transaction feed)
* Deep learning model comparison (autoencoders for anomaly detection)
* SHAP-based explainability layer for flagged transactions
* Deployment (Docker + cloud hosting)

**🎤 Conclusion**

FraudShield AI demonstrates a complete, role-based banking fraud monitoring platform: an offline-trained and comparison-justified ML model, a real-time detection pipeline, and a full fraud analyst workflow — from live transaction scoring to alert resolution — rather than a standalone machine learning experiment.
