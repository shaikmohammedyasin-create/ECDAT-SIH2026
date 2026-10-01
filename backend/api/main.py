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

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse

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
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration supporting cloud deployments (Vercel, Render, Railway) & local dev
allowed_origins_env = os.environ.get("ALLOWED_ORIGINS")
allowed_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]
if allowed_origins_env:
    allowed_origins.extend([orig.strip() for orig in allowed_origins_env.split(",") if orig.strip()])

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins if allowed_origins_env else ["*"],
    allow_origin_regex=r"https?://.*" if not allowed_origins_env else None,
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
        "version": "1.0.0",
        "air_gap": "enforced"
    }


# Static frontend serving directory
dist_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist"))

@app.get("/", include_in_schema=False)
async def root_index():
    index_file = os.path.join(dist_dir, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    from starlette.responses import RedirectResponse
    return RedirectResponse(url="/docs")


@app.get("/api", include_in_schema=False)
def api_index():
    return {
        "service": "ECDAT Security Workstation API",
        "status": "online",
        "docs": "/docs",
        "health": "/health",
        "message": "ECDAT API is running. Access /docs for interactive Swagger UI."
    }
if os.path.exists(dist_dir):
    assets_dir = os.path.join(dist_dir, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa(full_path: str):
        if (
            full_path.startswith("api/")
            or full_path == "api"
            or full_path.startswith("docs")
            or full_path.startswith("redoc")
            or full_path.startswith("openapi.json")
            or full_path == "health"
        ):
            raise HTTPException(status_code=404, detail="Not Found")
        
        file_path = os.path.join(dist_dir, full_path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        index_file = os.path.join(dist_dir, "index.html")
        if os.path.exists(index_file):
            return FileResponse(index_file)
        raise HTTPException(status_code=404, detail="Frontend build not found")


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    uvicorn.run("backend.api.main:app", host=host, port=port, reload=False)
