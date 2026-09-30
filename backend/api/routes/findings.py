"""
Findings Route Handler.
GET /api/findings/{id} - Deep forensic inspection of a specific cryptographic finding.
"""
import os
from fastapi import APIRouter, HTTPException
from backend.api.state import state
from backend.api.schemas import FindingDetail

router = APIRouter(prefix="/api/findings", tags=["findings"])


@router.get("/{finding_id}", response_model=FindingDetail)
def get_finding_detail(finding_id: int):
    assets = state.assets
    if finding_id < 0 or finding_id >= len(assets):
        raise HTTPException(status_code=404, detail=f"Finding ID {finding_id} not found (total: {len(assets)})")

    a = assets[finding_id]
    snippet = a.source_snippet or f"# [AST Occurrence]\n{a.algorithm} usage detected at line {a.line_number}"

    return FindingDetail(
        id=finding_id,
        rule_id=a.rule_id or "ECDAT-SRC-001",
        algorithm=a.algorithm,
        primitive=a.primitive,
        key_size=str(a.key_size) if a.key_size else "N/A",
        mode=a.mode or "N/A",
        padding=a.padding or "N/A",
        asset_type=a.asset_type.value,
        usage=a.usage.value,
        confidence=a.confidence,
        file_path=a.file_path,
        file_name=os.path.basename(a.file_path),
        line_number=a.line_number,
        source_snippet=snippet,
        quantum_status=a.quantum_status.value,
        quantum_vuln_class=a.quantum_vuln_class.value,
        hndl_risk=a.hndl_risk,
        tnfl_risk=a.tnfl_risk,
        why_risky=a.why_risky or "",
        mosca_margin=round(a.mosca_margin, 1) if a.mosca_margin is not None else None,
        mosca_at_risk=a.mosca_at_risk,
        x_lifetime=state.x_lifetime,
        y_migration=state.y_migration,
        scenario_year=state.scenario_year,
        risk_score=round(a.risk_score, 1),
        risk_band=a.risk_band,
        hygiene_critical=a.hygiene_critical,
        exposure=a.exposure,
        recommendation=a.recommendation or "",
        hybrid_option=a.hybrid_option,
        standard=a.standard,
        migration_effort=a.migration_effort,
        migration_path=a.migration_path or []
    )
