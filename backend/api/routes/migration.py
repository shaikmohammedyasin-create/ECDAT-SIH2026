"""
Migration Guidance Route Handler.
GET /api/migration - Deterministic PQC transition recommendations based on NIST FIPS 203/204/205.
"""
from fastapi import APIRouter
from backend.api.state import state
from backend.api.schemas import MigrationResponse, MigrationItem

router = APIRouter(prefix="/api/migration", tags=["migration"])


@router.get("", response_model=MigrationResponse)
def get_migration_guidance():
    assets = state.assets
    seen = set()
    items = []

    for a in sorted(assets, key=lambda x: x.risk_score, reverse=True):
        sig = (a.algorithm, a.usage.value)
        if sig not in seen and a.recommendation:
            seen.add(sig)
            target = a.recommendation.split(":")[-1].strip() if ":" in a.recommendation else a.recommendation
            strategy = "Hybrid Transition (Dual-Cert/KEM)" if a.hybrid_option else "Direct Primitive Replacement"
            items.append(MigrationItem(
                algorithm=a.algorithm,
                primitive=a.usage.value,
                risk_score=round(a.risk_score, 1),
                risk_band=a.risk_band,
                recommended_target=target,
                migration_strategy=strategy,
                standard=a.standard or "NIST PQC Standards",
                effort=a.migration_effort or "Moderate",
                migration_path=a.migration_path or []
            ))

    standards_dict = {
        "FIPS_203": "NIST FIPS 203: Module-Lattice-Based Key-Encapsulation Mechanism Standard (ML-KEM)",
        "FIPS_204": "NIST FIPS 204: Module-Lattice-Based Digital Signature Standard (ML-DSA)",
        "FIPS_205": "NIST FIPS 205: Stateless Hash-Based Digital Signature Standard (SLH-DSA)",
        "SP_800_56C": "NIST SP 800-56C Rev 2: Recommendation for Key-Derivation Methods in Key-Establishment Schemes",
    }

    # Calculate actual summary metrics across active scanned codebase
    imm_assets = [a for a in assets if a.quantum_status.value == "Vulnerable"]
    hyb_assets = [a for a in assets if a.hybrid_option]
    dep_assets = [a for a in assets if a.quantum_status.value == "Legacy-broken"]
    comp_assets = [
        a for a in assets
        if a.quantum_status.value in ("Safe", "PQC-ready") or a.quantum_vuln_class.value == "QUANTUM_SAFE"
    ]

    summary = {
        "immediate_count": len(imm_assets),
        "immediate_algos": sorted(list(set(a.algorithm for a in imm_assets))),
        "hybrid_count": len(hyb_assets),
        "hybrid_algos": sorted(list(set(a.algorithm for a in hyb_assets))),
        "deprecate_count": len(dep_assets),
        "deprecate_algos": sorted(list(set(a.algorithm for a in dep_assets))),
        "compliant_count": len(comp_assets),
        "compliant_algos": sorted(list(set(a.algorithm for a in comp_assets))),
    }

    return MigrationResponse(matrix=items, standards=standards_dict, summary=summary)
