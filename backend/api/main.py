"""
ECDAT Security Workstation — FastAPI Backend Entry Point.
SIH 2026 | PS ID 26164 | NTRO

Architecture:
  React + TypeScript + Vite + Stitch UI  (Frontend)
                     │
                 REST API
                     ▼
                 FastAPI                (Backend API Layer)
                     │
                     ▼
           Existing ECDAT Python Engine (Discovery, Normalization, Quantum, Mosca, Risk, PQC, CBOM)
"""
import sys
import os

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes import (
    dashboard,
    scans,
    inventory,
    findings,
    mosca,
    risk,
    migration,
    cbom,
    reports,
    terminal,
    settings
)

app = FastAPI(
    title="ECDAT Security Workstation API",
    description="Enterprise Cryptographic Discovery & Analysis Tool API — NTRO PS-ID 26164",
    version="2.4.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration for local Vite development
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API Routers
app.include_router(dashboard.router)
app.include_router(scans.router)
app.include_router(inventory.router)
app.include_router(findings.router)
app.include_router(mosca.router)
app.include_router(risk.router)
app.include_router(migration.router)
app.include_router(cbom.router)
app.include_router(reports.router)
app.include_router(terminal.router)
app.include_router(settings.router)


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "ECDAT Security Workstation API",
        "version": "2.4.0",
        "air_gap": "enforced"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.api.main:app", host="0.0.0.0", port=8000, reload=True)
