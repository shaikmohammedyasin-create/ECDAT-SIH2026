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

    # Calculate actual 5-factor averages across active scanned codebase
    q_sum, c_sum, e_sum, d_sum, ag_sum = 0.0, 0.0, 0.0, 0.0, 0.0
    n = len(assets) if assets else 1
    crit_map = {"Critical": 1.0, "High": 0.75, "Med": 0.5, "Medium": 0.5, "Low": 0.25}
    exp_map = {"External": 1.0, "Internal": 0.6, "Air-gapped": 0.3, "Offline": 0.3}
    sens_map = {"Archival": 1.0, "VL": 1.0, "L": 0.8, "M": 0.55, "S": 0.3}

    for a in assets:
        q_val = a.quantum_status.value
        qv = 1.0 if q_val == "Vulnerable" else (0.7 if q_val == "Legacy-broken" else (0.5 if q_val == "Weakened" else 0.0))
        if a.mosca_at_risk and q_val in ("Vulnerable", "Weakened"):
            qv = max(qv, 0.9)
        q_sum += qv
        c_sum += crit_map.get(a.criticality, 0.5)
        e_sum += exp_map.get(a.exposure, 0.6)
        d_sum += sens_map.get(a.lifetime, 0.55)
        ag = 0.4 if a.asset_type.value == "Certificate" else (0.3 if a.asset_type.value in ("Algorithm", "Protocol") else 0.8)
        ag_sum += ag

    factor_bd = {
        "quantum_exposure": round(q_sum / n, 2),
        "business_criticality": round(c_sum / n, 2),
        "exposure_surface": round(e_sum / n, 2),
        "data_sensitivity": round(d_sum / n, 2),
        "crypto_agility": round(ag_sum / n, 2),
        "inversed_agility": round(1.0 - (ag_sum / n), 2),
    }

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
        factor_breakdown=factor_bd,
        top_findings=top_items
    )
