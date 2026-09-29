"""Pydantic v2 data models for cryptographic assets."""
from __future__ import annotations
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field
import uuid


class AlgorithmFamily(str, Enum):
    ASYMMETRIC = "Asymmetric"
    SYMMETRIC = "Symmetric"
    HASH = "Hash"
    MAC = "MAC"
    KEY_DERIVATION = "Key Derivation"
    PROTOCOL = "Protocol"
    UNKNOWN = "Unknown"


class UsageType(str, Enum):
    ENCRYPTION = "Encryption"
    DECRYPTION = "Decryption"
    KEY_EXCHANGE = "Key Exchange"
    DIGITAL_SIGNATURE = "Digital Signature"
    HASHING = "Hashing"
    MAC = "MAC"
    KEY_DERIVATION = "Key Derivation"
    CERTIFICATE = "Certificate"
    TLS = "TLS/SSL"
    DEPENDENCY = "Dependency"
    CONFIGURATION = "Configuration"
    UNKNOWN = "Unknown"


class Confidence(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class RiskLevel(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    NONE = "NONE"


class AssetType(str, Enum):
    ALGORITHM = "Algorithm"
    PROTOCOL = "Protocol"
    LIBRARY = "Library"
    CERTIFICATE = "Certificate"
    CONFIGURATION = "Configuration"
    KEY_MATERIAL = "Key Material"


class CryptoAsset(BaseModel):
    """Represents a single discovered cryptographic artefact."""
    asset_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    asset_type: AssetType = AssetType.ALGORITHM
    algorithm: str
    variant: Optional[str] = None
    key_size: Optional[int] = None          # bits
    mode: Optional[str] = None              # e.g., CBC, GCM, ECB
    library: Optional[str] = None
    library_version: Optional[str] = None
    file_path: str
    line_number: Optional[int] = None
    snippet: Optional[str] = None           # surrounding code/config context
    usage: UsageType = UsageType.UNKNOWN
    protocol: Optional[str] = None          # e.g., TLS 1.2, SSH
    confidence: Confidence = Confidence.MEDIUM
    algorithm_family: AlgorithmFamily = AlgorithmFamily.UNKNOWN

    # Risk fields (populated by risk engine)
    data_sensitivity: Optional[str] = None  # LOW/MEDIUM/HIGH/CRITICAL
    data_lifetime: Optional[int] = None     # years
    business_criticality: Optional[str] = None
    quantum_risk: Optional[RiskLevel] = None
    classical_risk: Optional[RiskLevel] = None
    risk_score: Optional[float] = None      # 0.0 - 10.0
    risk_level: Optional[RiskLevel] = None
    risk_explanation: Optional[str] = None
    mosca_violation: Optional[bool] = None
    mosca_explanation: Optional[str] = None
    migration_priority: Optional[RiskLevel] = None

    # Recommendation (populated by recommendation engine)
    recommendation: Optional[str] = None
    recommendation_detail: Optional[dict] = None
