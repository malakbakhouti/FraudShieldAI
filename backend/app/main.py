from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import Base, engine
from app.routers import websocket, transactions

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Bank Fraud Detection API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(websocket.router)
app.include_router(transactions.router)

@app.get("/")
def root():
    return {"status": "Bank Fraud Detection API running"}
