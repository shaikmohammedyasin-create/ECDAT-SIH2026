"""
Scans Route Handler.
POST /api/scans         - Triggers a new scan on the given path or test corpus.
POST /api/scans/upload  - Accepts a ZIP, single source file, or any file for scanning.
POST /api/scans/paste   - Accepts raw pasted code text for scanning.
GET  /api/scans/status  - Returns current scan execution state and stages.
"""
import os
import shutil
import tempfile
import zipfile
from typing import Optional
from fastapi import APIRouter, HTTPException, Query, UploadFile, File, Form
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
    path = path.strip().strip('"').strip("'")
    if path.startswith("http://") or path.startswith("https://"):
        path_lower = path.lower()
        if "cpython" in path_lower:
            target = os.path.abspath(os.path.join("tests", "external_targets", "cpython"))
            if os.path.exists(target):
                return target
        elif "openssl" in path_lower:
            target = os.path.abspath(os.path.join("tests", "external_targets", "openssl"))
            if os.path.exists(target):
                return target
        elif "openssh" in path_lower:
            target = os.path.abspath(os.path.join("tests", "external_targets", "openssh"))
            if os.path.exists(target):
                return target
        
        # Generic Git clone into external_targets directory
        repo_name = path.rstrip("/").split("/")[-1].replace(".git", "")
        dest = os.path.abspath(os.path.join("tests", "external_targets", repo_name))
        if os.path.exists(dest):
            return dest
        import subprocess
        try:
            subprocess.run(["git", "clone", "--depth", "1", path, dest], check=True, timeout=60, capture_output=True)
            return dest
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to clone external repository {path}: {e}")

    if ".." in path:
        raise HTTPException(status_code=400, detail="Path traversal tokens ('..') are prohibited.")
    if os.name != "nt" and len(path) >= 2 and path[1] == ":" and path[0].isalpha():
        raise HTTPException(
            status_code=400,
            detail=f"Windows host path '{path}' cannot be accessed directly inside this Linux/Docker container. Please click 'Browse & Select Folder' in the UI to choose the folder directly from your PC."
        )
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


@router.post("/upload", response_model=ScanStatusResponse)
async def upload_scan(
    file: UploadFile = File(...),
    scenario_year: int = Form(2035),
    x_lifetime: float = Form(10.0),
    y_migration: float = Form(3.0),
):
    """Accept a file (ZIP archive or single source file) and run the full ECDAT pipeline."""
    filename = file.filename or "uploaded_file"
    # Sanitize filename
    safe_name = os.path.basename(filename.replace("\\", "/"))
    if not safe_name:
        raise HTTPException(status_code=400, detail="Invalid filename.")

    tmp_dir = tempfile.mkdtemp(prefix="ecdat_upload_")
    try:
        dest_path = os.path.join(tmp_dir, safe_name)
        contents = await file.read()
        if len(contents) > 500 * 1024 * 1024:  # 500 MB cap
            raise HTTPException(status_code=413, detail="Uploaded file exceeds 500 MB limit.")
        with open(dest_path, "wb") as f:
            f.write(contents)

        # If ZIP, extract into a subdirectory and scan that
        if safe_name.lower().endswith(".zip"):
            extract_dir = os.path.join(tmp_dir, "extracted")
            os.makedirs(extract_dir, exist_ok=True)
            try:
                with zipfile.ZipFile(dest_path, "r") as zf:
                    # Zip-slip protection
                    for member in zf.infolist():
                        member_path = os.path.realpath(os.path.join(extract_dir, member.filename))
                        if not member_path.startswith(os.path.realpath(extract_dir)):
                            raise HTTPException(status_code=400, detail="ZIP contains path traversal entry.")
                    zf.extractall(extract_dir)
            except zipfile.BadZipFile:
                raise HTTPException(status_code=400, detail="Uploaded file is not a valid ZIP archive.")
            scan_target = extract_dir
        else:
            # Single file — scan the temp dir containing the file
            scan_target = tmp_dir

        state.run_scan(
            directory=scan_target,
            scenario_year=scenario_year,
            x_lifetime=x_lifetime,
            y_migration=y_migration,
        )
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

    return ScanStatusResponse(
        scan_id=state.scan_id,
        scan_in_progress=False,
        current_stage="COMPLETE",
        target_path=f"<uploaded: {safe_name}>",
        total_assets=len(state.assets),
        metrics=state.metrics,
    )


@router.post("/paste", response_model=ScanStatusResponse)
async def paste_scan(
    code: str = Form(...),
    filename: str = Form("snippet.py"),
    scenario_year: int = Form(2035),
    x_lifetime: float = Form(10.0),
    y_migration: float = Form(3.0),
):
    """Accept pasted source code text and run the full ECDAT pipeline."""
    safe_name = os.path.basename(filename.replace("\\", "/")) or "snippet.py"
    if len(code) > 10 * 1024 * 1024:  # 10 MB text cap
        raise HTTPException(status_code=413, detail="Pasted code exceeds 10 MB limit.")

    tmp_dir = tempfile.mkdtemp(prefix="ecdat_paste_")
    try:
        dest_path = os.path.join(tmp_dir, safe_name)
        with open(dest_path, "w", encoding="utf-8", errors="replace") as f:
            f.write(code)

        state.run_scan(
            directory=tmp_dir,
            scenario_year=scenario_year,
            x_lifetime=x_lifetime,
            y_migration=y_migration,
        )
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

    return ScanStatusResponse(
        scan_id=state.scan_id,
        scan_in_progress=False,
        current_stage="COMPLETE",
        target_path=f"<pasted: {safe_name}>",
        total_assets=len(state.assets),
        metrics=state.metrics,
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

