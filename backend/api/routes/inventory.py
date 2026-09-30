"""
Inventory Route Handler.
GET /api/inventory - Filtered, searched, and paginated cryptographic assets list.
"""
import os
from typing import Optional
from fastapi import APIRouter, Query
from backend.api.state import state
from backend.api.schemas import InventoryResponse, InventoryItem

router = APIRouter(prefix="/api/inventory", tags=["inventory"])


@router.get("", response_model=InventoryResponse)
def get_inventory(
    search: Optional[str] = Query(None, description="Search term for algorithm, file, rule ID"),
    algorithm: Optional[str] = Query(None, description="Filter by algorithm name"),
    quantum_status: Optional[str] = Query(None, description="Filter by quantum status"),
    threat: Optional[str] = Query(None, description="Filter by threat flag HNDL/TNFL"),
    risk_band: Optional[str] = Query(None, description="Filter by risk band Critical/High/Medium/Low"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500)
):
    assets = state.assets
    all_algos = sorted(list(set(a.algorithm for a in assets)))
    all_quantum = sorted(list(set(a.quantum_status.value for a in assets)))
    all_threats = ["HNDL", "TNFL", "None"]
    all_bands = ["Critical", "High", "Medium", "Low", "Info"]

    items = []
    for idx, a in enumerate(assets):
        threat_str = "HNDL" if a.hndl_risk else ("TNFL" if a.tnfl_risk else "None")

        # Filters
        if algorithm and algorithm != "All" and a.algorithm != algorithm:
            continue
        if quantum_status and quantum_status != "All" and a.quantum_status.value != quantum_status:
            continue
        if threat and threat != "All" and threat_str != threat:
            continue
        if risk_band and risk_band != "All" and a.risk_band != risk_band:
            continue

        f_name = os.path.basename(a.file_path)
        if search:
            q = search.lower()
            if not (q in a.algorithm.lower() or q in f_name.lower() or q in (a.rule_id or "").lower() or q in a.primitive.lower()):
                continue

        items.append(InventoryItem(
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
            file=f_name,
            file_path=a.file_path,
            line=a.line_number
        ))

    total = len(items)
    start = (page - 1) * page_size
    end = start + page_size
    paged_items = items[start:end]

    return InventoryResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=paged_items,
        algorithms=all_algos,
        quantum_classes=all_quantum,
        threat_flags=all_threats,
        risk_bands=all_bands
    )
