"""
Dashboard Route Handler.
GET /api/dashboard - Returns executive summary metrics, risk distribution, quantum exposure, recent findings.
"""
import os
from fastapi import APIRouter
from backend.api.state import state
from backend.api.schemas import DashboardResponse, MetricSummary, RecentFinding, MigrationPriorityItem

router = APIRouter(prefix="/api", tags=["dashboard"])


@router.get("/dashboard", response_model=DashboardResponse)
def get_dashboard_summary():
    assets = state.assets
    m = state.metrics

    total_assets = len(assets)
    shor_vuln = sum(1 for a in assets if a.quantum_status.value == "Vulnerable")
    grover_weak = sum(1 for a in assets if a.quantum_status.value == "Weakened")
    classical_broken = sum(1 for a in assets if a.quantum_status.value == "Legacy-broken")
    safe_count = sum(1 for a in assets if a.quantum_status.value == "Quantum-safe")
    mosca_viol = sum(1 for a in assets if a.mosca_at_risk)
    crit_count = sum(1 for a in assets if a.risk_band == "Critical")
    high_count = sum(1 for a in assets if a.risk_band == "High")
    med_count = sum(1 for a in assets if a.risk_band == "Medium")
    low_count = sum(1 for a in assets if a.risk_band in ("Low", "Info"))

    metric_summary = MetricSummary(
        total_assets=total_assets,
        quantum_vulnerable=shor_vuln,
        grover_weakened=grover_weak,
        classically_broken=classical_broken,
        mosca_violations=mosca_viol,
        critical_risk=crit_count,
        high_risk=high_count,
        medium_risk=med_count,
        scan_time_s=m.get("scan_time_s", 0.0)
    )

    risk_dist = {
        "Critical": crit_count,
        "High": high_count,
        "Medium": med_count,
        "Low": low_count,
    }

    quantum_dist = {
        "SHOR_BROKEN": shor_vuln,
        "GROVER_WEAKENED": grover_weak,
        "QUANTUM_SAFE": safe_count,
        "CLASSICALLY_BROKEN": classical_broken,
    }

    # Top recent/critical findings
    sorted_assets = sorted(enumerate(assets), key=lambda x: x[1].risk_score, reverse=True)
    recent = []
    for idx, a in sorted_assets[:6]:
        threat_str = "HNDL" if a.hndl_risk else ("TNFL" if a.tnfl_risk else "None")
        recent.append(RecentFinding(
            id=idx,
            rule_id=a.rule_id or "ECDAT-SRC-001",
            algorithm=a.algorithm,
            primitive=a.primitive,
            file_path=a.file_path,
            file_name=os.path.basename(a.file_path),
            line_number=a.line_number,
            confidence=a.confidence,
            quantum_status=a.quantum_status.value,
            risk_score=round(a.risk_score, 1),
            risk_band=a.risk_band,
            threat=threat_str,
            usage=a.usage.value
        ))

    # Migration priority items
    mig_priority = []
    seen_algos = set()
    for _, a in sorted_assets:
        if a.algorithm not in seen_algos and a.recommendation:
            seen_algos.add(a.algorithm)
            target = a.recommendation.split(":")[-1].strip() if ":" in a.recommendation else a.recommendation[:50]
            mig_priority.append(MigrationPriorityItem(
                algorithm=a.algorithm,
                usage=a.usage.value,
                risk=f"{a.risk_score:.1f} ({a.risk_band})",
                risk_score=round(a.risk_score, 1),
                recommendation=target,
                priority=a.risk_band
            ))
        if len(mig_priority) >= 5:
            break

    val = state.get_validation()
    cbom_status = {
        "valid": val.get("valid", True),
        "spec_version": "1.6",
        "component_count": total_assets,
        "errors": val.get("errors", []),
        "schema": "bom-1.6.schema.json"
    }

    return DashboardResponse(
        metrics=metric_summary,
        risk_distribution=risk_dist,
        quantum_exposure=quantum_dist,
        recent_findings=recent,
        migration_priority=mig_priority,
        cbom_status=cbom_status,
        target_path=state.scan_path,
        status="Complete" if assets else "Idle"
    )
