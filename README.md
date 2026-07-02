**FraudShield AI**

Système full-stack de détection de fraude bancaire en temps réel, combinant Machine Learning et une architecture de streaming pour identifier les transactions suspectes.

## Stack technique

| Couche | Technologies |
|---|---|
| Frontend | Angular 22, Chart.js/ng2-charts, WebSocket |
| Backend | Python, FastAPI, WebSocket, SQLAlchemy |
| ML | Scikit-learn (Random Forest), imbalanced-learn (SMOTE) |
| Base de données | PostgreSQL |

## Architecture

```
frontend/    → Dashboard Angular temps réel (transactions live + alertes)
backend/     → API FastAPI (WebSocket + REST) + service de scoring ML
ml/          → Notebook d'entraînement du modèle (exploration, preprocessing, évaluation)
```

## Fonctionnement

1. Un flux de transactions simulées est généré et envoyé via WebSocket.
2. Chaque transaction est scorée en temps réel par un modèle Random Forest entraîné sur le dataset [Credit Card Fraud Detection](https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud) (284 807 transactions, 0.17% de fraudes).
3. Le déséquilibre des classes est traité avec SMOTE (oversampling).
4. Les transactions et leur score de fraude sont persistées en PostgreSQL et poussées au frontend en temps réel.

## Modèle ML

- **Algorithme** : Random Forest (`class_weight='balanced'`, 200 arbres)
- **Rééquilibrage** : SMOTE sur le jeu d'entraînement
- **Métriques d'évaluation** : ROC-AUC, PR-AUC (adaptées au fort déséquilibre des classes), matrice de confusion

## Lancer le projet

**Backend**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

**Frontend**
```bash
cd frontend
npm install
ng serve
```

**Modèle ML**
```bash
cd ml
jupyter notebook fraud_detection_model.ipynb
```

## Auteur

Malak Bakhouti — 4ème année Ingénierie Informatique, EMSI Rabat
