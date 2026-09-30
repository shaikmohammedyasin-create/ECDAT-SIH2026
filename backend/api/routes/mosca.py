"""
Mosca Simulator Route Handler.
GET  /api/mosca - Returns current Mosca state and planning horizon metrics.
POST /api/mosca/simulate - Simulates X + Y > Z with updated inputs, optionally re-computing active inventory.
"""
from fastapi import APIRouter
from backend.api.state import state
from backend.api.schemas import MoscaSimulateRequest, MoscaSimulateResponse

router = APIRouter(prefix="/api/mosca", tags=["mosca"])

CURRENT_YEAR = 2026


@router.get("", response_model=MoscaSimulateResponse)
def get_mosca_state():
    z_horizon = state.scenario_year - CURRENT_YEAR
    req_window = state.x_lifetime + state.y_migration
    margin = z_horizon - req_window
    at_risk = margin < 0
    viol_count = sum(1 for a in state.assets if a.mosca_at_risk)

    return MoscaSimulateResponse(
        scenario_year=state.scenario_year,
        current_year=CURRENT_YEAR,
        x_lifetime=state.x_lifetime,
        y_migration=state.y_migration,
        required_window=round(req_window, 1),
        z_horizon=z_horizon,
        security_margin=round(margin, 1),
        at_risk=at_risk,
        violations_count=viol_count,
        total_assets=len(state.assets)
    )


@router.post("/simulate", response_model=MoscaSimulateResponse)
def simulate_mosca(req: MoscaSimulateRequest):
    if req.recompute_scan:
        state.run_scan(
            directory=state.scan_path,
            scenario_year=req.scenario_year,
            x_lifetime=req.x_lifetime,
            y_migration=req.y_migration
        )
    else:
        state.scenario_year = req.scenario_year
        state.x_lifetime = req.x_lifetime
        state.y_migration = req.y_migration

    z_horizon = req.scenario_year - CURRENT_YEAR
    req_window = req.x_lifetime + req.y_migration
    margin = z_horizon - req_window
    at_risk = margin < 0
    viol_count = sum(1 for a in state.assets if a.mosca_at_risk)

    return MoscaSimulateResponse(
        scenario_year=req.scenario_year,
        current_year=CURRENT_YEAR,
        x_lifetime=req.x_lifetime,
        y_migration=req.y_migration,
        required_window=round(req_window, 1),
        z_horizon=z_horizon,
        security_margin=round(margin, 1),
        at_risk=at_risk,
        violations_count=viol_count,
        total_assets=len(state.assets)
    )
