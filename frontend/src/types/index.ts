export interface MetricSummary {
  total_assets: number;
  quantum_vulnerable: number;
  grover_weakened: number;
  classically_broken: number;
  mosca_violations: number;
  critical_risk: number;
  high_risk: number;
  medium_risk: number;
  scan_time_s: number;
}

export interface RecentFinding {
  id: number;
  rule_id: string;
  algorithm: string;
  primitive: string;
  file_path: string;
  file_name: string;
  line_number: number;
  confidence: string;
  quantum_status: string;
  risk_score: number;
  risk_band: string;
  threat: string;
  usage: string;
}

export interface MigrationPriorityItem {
  algorithm: string;
  usage: string;
  risk: string;
  risk_score: number;
  recommendation: string;
  priority: string;
}

export interface DashboardData {
  metrics: MetricSummary;
  risk_distribution: Record<string, number>;
  quantum_exposure: Record<string, number>;
  recent_findings: RecentFinding[];
  migration_priority: MigrationPriorityItem[];
  cbom_status: {
    valid: boolean;
    spec_version: string;
    component_count: number;
    errors: string[];
    schema: string;
  };
  target_path: string;
  status: string;
}

export interface InventoryItem {
  id: number;
  rule_id: string;
  algorithm: string;
  primitive: string;
  key_size: string;
  mode: string;
  padding: string;
  type: string;
  usage: string;
  quantum: string;
  threat: string;
  risk_score: number;
  risk_band: string;
  mosca_margin: number | null;
  confidence: string;
  file: string;
  file_path: string;
  line: number;
}

export interface InventoryResponse {
  total: number;
  page: number;
  page_size: number;
  items: InventoryItem[];
  algorithms: string[];
  quantum_classes: string[];
  threat_flags: string[];
  risk_bands: string[];
}

export interface FindingDetail {
  id: number;
  rule_id: string;
  algorithm: string;
  primitive: string;
  key_size: string;
  mode: string;
  padding: string;
  asset_type: string;
  usage: string;
  confidence: string;
  file_path: string;
  file_name: string;
  line_number: number;
  source_snippet: string;
  quantum_status: string;
  quantum_vuln_class: string;
  hndl_risk: boolean;
  tnfl_risk: boolean;
  why_risky: string;
  mosca_margin: number | null;
  mosca_at_risk: boolean;
  x_lifetime: number;
  y_migration: number;
  scenario_year: number;
  risk_score: number;
  risk_band: string;
  hygiene_critical: boolean;
  exposure: string;
  recommendation: string;
  hybrid_option: string | null;
  standard: string | null;
  migration_effort: string | null;
  migration_path: string[];
}

export interface MoscaState {
  scenario_year: number;
  current_year: number;
  x_lifetime: number;
  y_migration: number;
  required_window: number;
  z_horizon: number;
  security_margin: number;
  at_risk: boolean;
  violations_count: number;
  total_assets: number;
}

export interface RiskAnalysisData {
  formula: string;
  weights: Record<string, number>;
  average_score: number;
  risk_distribution: Record<string, number>;
  hygiene_critical_count: number;
  top_findings: InventoryItem[];
}

export interface MigrationItem {
  algorithm: string;
  primitive: string;
  risk_score: number;
  risk_band: string;
  recommended_target: string;
  migration_strategy: string;
  standard: string;
  effort: string;
  migration_path: string[];
}

export interface MigrationResponse {
  matrix: MigrationItem[];
  standards: Record<string, string>;
}

export interface CBOMData {
  cbom: any;
  validation: {
    valid: boolean;
    errors: string[];
    schema?: string;
  };
  component_count: number;
}

export interface ReportDeliverable {
  id: string;
  name: string;
  filename: string;
  mime: string;
  available: boolean;
}

export interface ReportsMetadata {
  total_deliverables: number;
  available_formats: ReportDeliverable[];
  validation_status: string;
  total_assets: number;
}

export interface TerminalLog {
  timestamp: string;
  level: string;
  message: string;
}

export interface SettingsData {
  profile: string;
  ast_enabled: boolean;
  bytecode_scanner_enabled: boolean;
  comment_filtering: boolean;
  ignore_paths: string[];
  risk_thresholds: Record<string, number>;
  air_gap_enforced: boolean;
  zero_key_persistence: boolean;
  strict_sandbox: boolean;
}
