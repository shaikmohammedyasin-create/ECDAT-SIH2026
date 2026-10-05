"""
Pydantic Schemas for ECDAT FastAPI API.
Matches TypeScript types in frontend.
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class ScanRequest(BaseModel):
    path: Optional[str] = ""
    use_corpus: Optional[bool] = False
    scenario_year: Optional[int] = 2035
    x_lifetime: Optional[float] = 10.0
    y_migration: Optional[float] = 3.0


class ScanStatusResponse(BaseModel):
    scan_id: str
    scan_in_progress: bool
    current_stage: str
    target_path: str
    total_assets: int
    metrics: Dict[str, Any]


class MetricSummary(BaseModel):
    total_assets: int
    quantum_vulnerable: int
    grover_weakened: int
    classically_broken: int
    quantum_safe: Optional[int] = 0
    mosca_violations: int
    critical_risk: int
    high_risk: int
    medium_risk: int
    scan_time_s: float


class RecentFinding(BaseModel):
    id: int
    rule_id: str
    algorithm: str
    primitive: str
    file_path: str
    file_name: str
    line_number: int
    confidence: str
    quantum_status: str
    risk_score: float
    risk_band: str
    threat: str
    usage: str


class MigrationPriorityItem(BaseModel):
    algorithm: str
    usage: str
    risk: str
    risk_score: float
    recommendation: str
    priority: str


class DashboardResponse(BaseModel):
    metrics: MetricSummary
    risk_distribution: Dict[str, int]
    quantum_exposure: Dict[str, int]
    recent_findings: List[RecentFinding]
    migration_priority: List[MigrationPriorityItem]
    cbom_status: Dict[str, Any]
    target_path: str
    status: str


class InventoryItem(BaseModel):
    id: int
    rule_id: str
    algorithm: str
    primitive: str
    key_size: Optional[str] = "N/A"
    mode: Optional[str] = "N/A"
    padding: Optional[str] = "N/A"
    type: str
    usage: str
    quantum: str
    threat: str
    risk_score: float
    risk_band: str
    mosca_margin: Optional[float] = None
    confidence: str
    file: str
    file_path: str
    line: int


class InventoryResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[InventoryItem]
    algorithms: List[str]
    quantum_classes: List[str]
    threat_flags: List[str]
    risk_bands: List[str]


class FindingDetail(BaseModel):
    id: int
    rule_id: str
    algorithm: str
    primitive: str
    key_size: Optional[str] = "N/A"
    mode: Optional[str] = "N/A"
    padding: Optional[str] = "N/A"
    asset_type: str
    usage: str
    confidence: str
    file_path: str
    file_name: str
    line_number: int
    source_snippet: str
    quantum_status: str
    quantum_vuln_class: str
    hndl_risk: bool
    tnfl_risk: bool
    why_risky: Optional[str] = ""
    mosca_margin: Optional[float] = None
    mosca_at_risk: bool
    x_lifetime: float
    y_migration: float
    scenario_year: int
    risk_score: float
    risk_band: str
    hygiene_critical: bool
    exposure: str
    recommendation: Optional[str] = ""
    hybrid_option: Optional[str] = None
    standard: Optional[str] = None
    migration_effort: Optional[str] = None
    migration_path: List[str] = []


class MoscaSimulateRequest(BaseModel):
    scenario_year: int = 2035
    x_lifetime: float = 10.0
    y_migration: float = 3.0
    recompute_scan: Optional[bool] = False


class MoscaSimulateResponse(BaseModel):
    scenario_year: int
    current_year: int
    x_lifetime: float
    y_migration: float
    required_window: float
    z_horizon: int
    security_margin: float
    at_risk: bool
    violations_count: int
    total_assets: int


class FactorBreakdown(BaseModel):
    quantum_exposure: float
    business_criticality: float
    exposure_surface: float
    data_sensitivity: float
    crypto_agility: float
    inversed_agility: float


class RiskAnalysisResponse(BaseModel):
    formula: str
    weights: Dict[str, float]
    average_score: float
    risk_distribution: Dict[str, int]
    hygiene_critical_count: int
    factor_breakdown: FactorBreakdown
    top_findings: List[InventoryItem]


class MigrationItem(BaseModel):
    algorithm: str
    primitive: str
    risk_score: float
    risk_band: str
    recommended_target: str
    migration_strategy: str
    standard: str
    effort: str
    migration_path: List[str]


class MigrationSummary(BaseModel):
    immediate_count: int
    immediate_algos: List[str]
    hybrid_count: int
    hybrid_algos: List[str]
    deprecate_count: int
    deprecate_algos: List[str]
    compliant_count: int
    compliant_algos: List[str]


class MigrationResponse(BaseModel):
    matrix: List[MigrationItem]
    standards: Dict[str, str]
    summary: MigrationSummary


class CBOMResponse(BaseModel):
    cbom: Dict[str, Any]
    validation: Dict[str, Any]
    component_count: int


class TerminalLogItem(BaseModel):
    timestamp: str
    level: str
    message: str


class SettingsResponse(BaseModel):
    profile: str
    target_path: str = ""
    scenario_year: int = 2035
    x_lifetime: float = 10.0
    y_migration: float = 3.0
    ast_enabled: bool = True
    bytecode_scanner_enabled: bool = True
    dependency_manifest_parser: bool = True
    cert_scanner_enabled: bool = True
    comment_filtering: bool = True
    ignore_paths: List[str] = []
    risk_weights: Dict[str, float] = {}
    risk_thresholds: Dict[str, float] = {}
    cyclonedx_version: str = "1.6"
    strict_validation: bool = True
    deterministic_bom_ref: bool = True
    air_gap_enforced: bool = True
    zero_key_persistence: bool = True
    strict_sandbox: bool = True
