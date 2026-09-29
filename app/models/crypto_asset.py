from enum import Enum
from typing import Optional, List, Dict
from pydantic import BaseModel


class AssetType(str, Enum):
    ALGORITHM = "Algorithm"
    KEY = "Key"
    CERTIFICATE = "Certificate"
    PROTOCOL = "Protocol"
    LIBRARY = "Library"


class QuantumStatus(str, Enum):
    VULNERABLE = "Vulnerable"              # SHOR_BROKEN equivalent
    WEAKENED = "Weakened"                  # GROVER_WEAKENED equivalent
    SAFE = "Safe"                          # QUANTUM_SAFE equivalent
    PQC_READY = "PQC-ready"
    LEGACY_BROKEN = "Legacy-broken"        # CLASSICALLY_BROKEN equivalent


# Source-of-truth quantum classes (kept for CBOM export / classification)
class QuantumVulnClass(str, Enum):
    SHOR_BROKEN = "SHOR_BROKEN"
    GROVER_WEAKENED = "GROVER_WEAKENED"
    QUANTUM_SAFE = "QUANTUM_SAFE"
    CLASSICALLY_BROKEN = "CLASSICALLY_BROKEN"


class UsageFunction(str, Enum):
    ENCRYPTION = "Encryption/Decryption"
    SIGNATURE = "Signature"
    HASH = "Hash/MAC"
    KEY_EXCHANGE = "Key Exchange"


class CryptoAsset(BaseModel):
    # Discovery fields
    asset_id: str
    asset_type: AssetType
    algorithm: str
    primitive: str
    key_size: Optional[int]
    mode: Optional[str]
    padding: Optional[str]
    curve: Optional[str]
    hash_algo: Optional[str]
    library: str
    library_version: Optional[str] = None
    file_path: str
    line_number: int
    source_snippet: str
    confidence: str  # HIGH, MEDIUM, LOW
    usage: UsageFunction
    rule_id: Optional[str] = None
    provenance: str = "OBSERVED"  # OBSERVED, INFERRED, UNKNOWN (source/code vs inferred)

    # Analysis fields
    quantum_status: QuantumStatus
    quantum_vuln_class: QuantumVulnClass = QuantumVulnClass.QUANTUM_SAFE
    hndl_risk: bool = False
    tnfl_risk: bool = False

    # Classification & Criticality
    lifetime: str  # S, M, L, VL (or Short/Medium/Long/Archival)
    criticality: str  # Critical, High, Med, Low
    exposure: str  # External, Internal, Air-gapped

    # Source-of-truth unified-schema fields
    data_sensitivity: str = "internal"       # public/internal/confidential/secret
    data_lifetime_years: Optional[float] = None
    business_criticality: Optional[int] = None  # 1-5
    migration_time_years: Optional[float] = None
    component_ref: Optional[str] = None
    application: str = "scanned-project"
    environment: str = "local"

    # Mosca
    mosca_margin: Optional[float] = None
    mosca_at_risk: bool = False

    # Risk Metrics
    risk_score: float = 0.0
    risk_band: str = "Info"  # Critical, High, Med, Low, Info
    hygiene_critical: bool = False

    # Recommendations
    recommendation: Optional[str] = None
    migration_path: Optional[List[str]] = None
    hybrid_option: Optional[str] = None
    why_risky: Optional[str] = None
    migration_effort: Optional[str] = None
    standard: Optional[str] = None

    # CBOM export per-asset
    cbom_ref: Optional[str] = None
