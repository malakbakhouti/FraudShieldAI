from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import Base, engine
from app.routers import websocket, transactions, import_router, auth, users, settings, import_router

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
app.include_router(import_router.router)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(settings.router)
app.include_router(import_router.router)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(settings.router)

@app.get("/")
def root():
    return {"status": "Bank Fraud Detection API running"}
