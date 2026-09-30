"""
Scans Route Handler.
POST /api/scans - Triggers a new scan on the given path or test corpus.
GET  /api/scans/status - Returns current scan execution state and stages.
"""
import os
from fastapi import APIRouter, HTTPException
from backend.api.state import state, DEFAULT_CORPUS
from backend.api.schemas import ScanRequest, ScanStatusResponse

router = APIRouter(prefix="/api/scans", tags=["scans"])


@router.post("", response_model=ScanStatusResponse)
def trigger_scan(req: ScanRequest):
    target = DEFAULT_CORPUS if req.use_corpus else os.path.abspath(req.path)
    if not os.path.exists(target):
        raise HTTPException(status_code=404, detail=f"Target path does not exist on disk: {target}")

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
