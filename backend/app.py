"""
Main FastAPI application entry point for Prize2Plate.
Run with:
    uvicorn app:app --reload
"""

from typing import Dict

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import CORS_ORIGINS, PROJECT_NAME, PROJECT_STATUS
from routes import alerts, alternatives, climate, foods

app = FastAPI(
    title=PROJECT_NAME,
    description=(
        "Hackathon backend for identifying food price shocks, supply signals, "
        "climate anomalies, and recommending affordable, nutritious alternatives."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(foods.router)
app.include_router(alerts.router)
app.include_router(alternatives.router)
app.include_router(climate.router)


@app.get("/", tags=["System"])
def root() -> Dict[str, str]:
    """Root status endpoint."""
    return {
        "project": PROJECT_NAME,
        "status": PROJECT_STATUS,
    }


@app.get("/health", tags=["System"])
def health_check() -> Dict[str, str]:
    """Health check endpoint."""
    return {
        "status": "healthy",
    }
