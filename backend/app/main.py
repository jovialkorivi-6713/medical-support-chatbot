from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
import os

from app.database.connection import init_db
from app.routers import auth, chat, symptom, report, hospital, medicine, mental_health

# Define application lifespan events (Startup/Shutdown)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize MongoDB and Beanie
    await init_db()
    yield
    # Shutdown logic (if any) can go here

app = FastAPI(
    title="MediAssist AI API",
    description="Backend API for MediAssist AI - A complete AI Medical Assistant Platform",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
origins = [
    "http://localhost:8501", # Streamlit default port
    "*" # Adjust this in production
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(chat.router, prefix="/api/v1/chat", tags=["AI Chatbot"])
app.include_router(symptom.router, prefix="/api/v1/symptoms", tags=["Symptom Checker"])
app.include_router(report.router)
app.include_router(hospital.router, prefix="/api/v1/hospital", tags=["Hospital Finder"])
app.include_router(medicine.router, prefix="/api/v1/medicine", tags=["Medicine Info"])
app.include_router(mental_health.router, prefix="/api/v1/mental_health", tags=["Mental Health"])

@app.get("/")
async def root():
    return {"message": "Welcome to MediAssist AI API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
# Trigger reload
