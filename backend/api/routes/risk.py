"""
Risk Analysis Route Handler.
GET /api/risk - 5-factor deterministic risk model breakdown, weights, distribution, and top ranked findings.
"""
import os
from fastapi import APIRouter
from backend.api.state import state
from backend.api.schemas import RiskAnalysisResponse, InventoryItem

router = APIRouter(prefix="/api/risk", tags=["risk"])


@router.get("", response_model=RiskAnalysisResponse)
def get_risk_analysis():
    assets = state.assets
    avg = sum(a.risk_score for a in assets) / len(assets) if assets else 0.0

    crit = sum(1 for a in assets if a.risk_band == "Critical")
    high = sum(1 for a in assets if a.risk_band == "High")
    med = sum(1 for a in assets if a.risk_band == "Medium")
    low = sum(1 for a in assets if a.risk_band in ("Low", "Info"))
    hygiene = sum(1 for a in assets if a.hygiene_critical or a.quantum_status.value == "Legacy-broken")

    sorted_assets = sorted(enumerate(assets), key=lambda x: x[1].risk_score, reverse=True)
    top_items = []
    for idx, a in sorted_assets[:10]:
        threat_str = "HNDL" if a.hndl_risk else ("TNFL" if a.tnfl_risk else "None")
        top_items.append(InventoryItem(
            id=idx,
            rule_id=a.rule_id or "ECDAT-SRC-001",
            algorithm=a.algorithm,
            primitive=a.primitive,
            key_size=str(a.key_size) if a.key_size else "N/A",
            mode=a.mode or "N/A",
            padding=a.padding or "N/A",
            type=a.asset_type.value,
            usage=a.usage.value,
            quantum=a.quantum_status.value,
            threat=threat_str,
            risk_score=round(a.risk_score, 1),
            risk_band=a.risk_band,
            mosca_margin=round(a.mosca_margin, 1) if a.mosca_margin is not None else None,
            confidence=a.confidence,
            file=os.path.basename(a.file_path),
            file_path=a.file_path,
            line=a.line_number
        ))

    return RiskAnalysisResponse(
        formula="RiskScore = 100 * (0.35 * QuantumExposure + 0.25 * BusinessCriticality + 0.15 * ExposureSurface + 0.15 * DataSensitivity + 0.10 * (1 - CryptoAgility))",
        weights={
            "quantum_exposure": 0.35,
            "business_criticality": 0.25,
            "exposure_surface": 0.15,
            "data_sensitivity": 0.15,
            "crypto_agility": 0.10
        },
        average_score=round(avg, 1),
        risk_distribution={
            "Critical": crit,
            "High": high,
            "Medium": med,
            "Low": low
        },
        hygiene_critical_count=hygiene,
        top_findings=top_items
    )
