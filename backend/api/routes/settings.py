"""
Settings & Security Policies Route Handler.
GET /api/settings - Returns workstation parameters, risk thresholds, and air-gap assurances.
"""
from fastapi import APIRouter
from backend.api.schemas import SettingsResponse
from backend.api.state import state

router = APIRouter(prefix="/api/settings", tags=["settings"])


@router.get("", response_model=SettingsResponse)
def get_workstation_settings():
    return SettingsResponse(
        profile="AST-Crypt-Strict (NTRO-SEC)",
        target_path=state.scan_path,
        scenario_year=state.scenario_year,
        x_lifetime=state.x_lifetime,
        y_migration=state.y_migration,
        ast_enabled=True,
        bytecode_scanner_enabled=True,
        dependency_manifest_parser=True,
        cert_scanner_enabled=True,
        comment_filtering=True,
        ignore_paths=[".git", "node_modules", "venv", "__pycache__", "dist", "build"],
        risk_weights={
            "quantum_exposure": 0.35,
            "business_criticality": 0.25,
            "exposure_surface": 0.15,
            "data_sensitivity": 0.15,
            "crypto_agility": 0.10
        },
        risk_thresholds={
            "critical": 80.0,
            "high": 60.0,
            "medium": 40.0,
            "low": 20.0
        },
        cyclonedx_version="1.6",
        strict_validation=True,
        deterministic_bom_ref=True,
        air_gap_enforced=True,
        zero_key_persistence=True,
        strict_sandbox=True
    )
