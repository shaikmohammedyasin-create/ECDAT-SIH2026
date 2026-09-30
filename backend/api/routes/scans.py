"""
Scans Route Handler.
POST /api/scans - Triggers a new scan on the given path or test corpus.
GET  /api/scans/status - Returns current scan execution state and stages.
"""
import os
from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from backend.api.state import state, DEFAULT_CORPUS
from backend.api.schemas import (
    ScanRequest,
    ScanStatusResponse,
    InventoryResponse,
    RiskAnalysisResponse,
    MoscaSimulateResponse,
    MigrationResponse,
    CBOMResponse
)
from backend.api.routes.inventory import get_inventory
from backend.api.routes.risk import get_risk_analysis
from backend.api.routes.mosca import get_mosca_state
from backend.api.routes.migration import get_migration_guidance
from backend.api.routes.cbom import get_cbom_data
from backend.api.routes.reports import get_reports_metadata

router = APIRouter(prefix="/api/scans", tags=["scans"])


def _validate_scan_path(path: str) -> str:
    if ".." in path:
        raise HTTPException(status_code=400, detail="Path traversal tokens ('..') are prohibited.")
    norm = os.path.abspath(os.path.normpath(path))
    if not os.path.exists(norm):
        raise HTTPException(status_code=404, detail=f"Target path does not exist on disk: {norm}")
    drive, rest = os.path.splitdrive(norm)
    rest_lower = rest.lower().replace("/", "\\")
    if rest_lower in ("\\", "") or rest_lower.startswith(("\\windows", "\\system32", "\\program files", "\\program files (x86)", "\\etc", "\\root", "\\sys", "\\proc")):
        raise HTTPException(status_code=400, detail="Scanning system root directories is prohibited for safety.")
    return norm


@router.post("", response_model=ScanStatusResponse)
def trigger_scan(req: ScanRequest):
    target = DEFAULT_CORPUS if req.use_corpus else _validate_scan_path(req.path)

    res = state.run_scan(
        directory=target,
        scenario_year=req.scenario_year,
        x_lifetime=req.x_lifetime,
        y_migration=req.y_migration
    )

    return ScanStatusResponse(
        scan_id=state.scan_id,
        scan_in_progress=False,
        current_stage="COMPLETE",
        target_path=state.scan_path,
        total_assets=len(state.assets),
        metrics=state.metrics
    )


@router.get("/status", response_model=ScanStatusResponse)
def get_scan_status():
    return ScanStatusResponse(
        scan_id=state.scan_id,
        scan_in_progress=state.scan_in_progress,
        current_stage=state.current_stage,
        target_path=state.scan_path,
        total_assets=len(state.assets),
        metrics=state.metrics
    )


@router.get("/{scan_id}", response_model=ScanStatusResponse)
def get_scan_by_id(scan_id: str):
    return ScanStatusResponse(
        scan_id=state.scan_id,
        scan_in_progress=state.scan_in_progress,
        current_stage=state.current_stage,
        target_path=state.scan_path,
        total_assets=len(state.assets),
        metrics=state.metrics
    )


@router.get("/{scan_id}/findings", response_model=InventoryResponse)
def get_scan_findings(
    scan_id: str,
    search: Optional[str] = Query(None),
    algorithm: Optional[str] = Query(None),
    quantum_status: Optional[str] = Query(None),
    threat: Optional[str] = Query(None),
    risk_band: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500)
):
    return get_inventory(search, algorithm, quantum_status, threat, risk_band, page, page_size)


@router.get("/{scan_id}/inventory", response_model=InventoryResponse)
def get_scan_inventory(
    scan_id: str,
    search: Optional[str] = Query(None),
    algorithm: Optional[str] = Query(None),
    quantum_status: Optional[str] = Query(None),
    threat: Optional[str] = Query(None),
    risk_band: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500)
):
    return get_inventory(search, algorithm, quantum_status, threat, risk_band, page, page_size)


@router.get("/{scan_id}/risk", response_model=RiskAnalysisResponse)
def get_scan_risk(scan_id: str):
    return get_risk_analysis()


@router.get("/{scan_id}/mosca", response_model=MoscaSimulateResponse)
def get_scan_mosca(scan_id: str, scenario_year: int = Query(2035)):
    return get_mosca_state()


@router.get("/{scan_id}/migration", response_model=MigrationResponse)
def get_scan_migration(scan_id: str):
    return get_migration_guidance()


@router.get("/{scan_id}/cbom", response_model=CBOMResponse)
def get_scan_cbom(scan_id: str):
    return get_cbom_data()


@router.get("/{scan_id}/reports")
def get_scan_reports(scan_id: str):
    return get_reports_metadata()

