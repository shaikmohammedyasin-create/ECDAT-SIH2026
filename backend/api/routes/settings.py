"""
Settings & Security Policies Route Handler.
GET /api/settings - Returns workstation parameters, risk thresholds, and air-gap assurances.
"""
from fastapi import APIRouter
from backend.api.schemas import SettingsResponse

router = APIRouter(prefix="/api/settings", tags=["settings"])


@router.get("", response_model=SettingsResponse)
def get_workstation_settings():
    return SettingsResponse(
        profile="AST-Crypt-Strict (NTRO-SEC)",
        ast_enabled=True,
        bytecode_scanner_enabled=True,
        comment_filtering=True,
        ignore_paths=[".git", "node_modules", "venv", "__pycache__", "dist", "build"],
        risk_thresholds={
            "critical": 80.0,
            "high": 60.0,
            "medium": 40.0,
            "low": 0.0
        },
        air_gap_enforced=True,
        zero_key_persistence=True,
        strict_sandbox=True
    )
