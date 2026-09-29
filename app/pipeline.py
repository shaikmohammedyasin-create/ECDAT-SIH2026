"""
End-to-end ECDAT scan pipeline.

REAL INPUT -> DISCOVERY (source/dependency/certificate/config)
           -> NORMALISATION -> QUANTUM CLASSIFICATION -> HNDL/TNFL
           -> MOSCA -> RISK -> RECOMMENDATION -> CBOM

Facilitates running a full scan of a directory and returning analysed assets.
"""
import os
import time
from typing import List, Tuple

from app.models.crypto_asset import CryptoAsset
from app.scanners.source_scanner import run_project_scan
from app.scanners.dependency_scanner import scan_dependency_file
from app.scanners.certificate_scanner import scan_certificate_file
from app.scanners.config_scanner import scan_config_file
from app.scanners.binary_scanner import scan_binary_file
from app.analysis.quantum_rules import apply_quantum_rules
from app.analysis.mosca import compute_mosca
from app.analysis.risk import calculate_risk_score
from app.analysis.recommendations import generate_recommendations


# File types routed to each scanner
SOURCE_EXTS = {".py", ".js", ".java", ".ts", ".jsx", ".tsx"}
DEP_FILENAMES = {
    "requirements.txt", "requirements-dev.txt", "pom.xml",
    "package.json", "package-lock.json", "pyproject.toml",
    "go.mod", "cargo.toml", "build.gradle"
}
CERT_EXTS = {".pem", ".crt", ".cer", ".der", ".p12", ".pfx", ".pub"}
CONFIG_EXTS = {".conf", ".cfg"}
CONFIG_NAMES = {"nginx.conf", "sshd_config", "openssl.cnf", "Dockerfile"}
BINARY_EXTS = {".class", ".jar", ".war"}


def _scan_source(directory: str) -> List[CryptoAsset]:
    return run_project_scan(directory)


def _scan_dependencies(directory: str) -> List[CryptoAsset]:
    out = []
    for root, _, files in os.walk(directory):
        if any(skip in root for skip in (".git", "node_modules", "venv", "__pycache__")):
            continue
        for f in files:
            if f.lower() in DEP_FILENAMES:
                fp = os.path.join(root, f)
                out.extend(scan_dependency_file(fp))
    return out


def _scan_certificates(directory: str) -> List[CryptoAsset]:
    out = []
    for root, _, files in os.walk(directory):
        if any(skip in root for skip in (".git", "node_modules", "venv", "__pycache__")):
            continue
        for f in files:
            if f.lower().endswith(tuple(CERT_EXTS)) or ".crt" in f.lower():
                out.extend(scan_certificate_file(os.path.join(root, f)))
    return out


def _scan_configs(directory: str) -> List[CryptoAsset]:
    out = []
    for root, _, files in os.walk(directory):
        if any(skip in root for skip in (".git", "node_modules", "venv", "__pycache__")):
            continue
        for f in files:
            base = f.lower()
            if base.endswith(tuple(CONFIG_EXTS)) or base in CONFIG_NAMES or "tls" in base:
                out.extend(scan_config_file(os.path.join(root, f)))
    return out


def _scan_binaries(directory: str) -> List[CryptoAsset]:
    out = []
    for root, _, files in os.walk(directory):
        if any(skip in root for skip in (".git", "node_modules", "venv", "__pycache__")):
            continue
        for f in files:
            if f.lower().endswith(tuple(BINARY_EXTS)):
                out.extend(scan_binary_file(os.path.join(root, f)))
    return out


def run_full_scan(
    directory: str,
    scenario_year: int = 2035,
    x_lifetime: float = 10.0,
    y_migration: float = 3.0,
    log_callback = None,
) -> Tuple[List[CryptoAsset], dict]:
    """
    Runs the complete discovery + analysis pipeline over a directory.
    Returns (processed_assets, metrics).
    """
    def _log(level: str, msg: str):
        if log_callback:
            log_callback(level, msg)

    t0 = time.time()
    _log("INFO", f"Initializing ECDAT engine. Target directory: {directory}")
    _log("INFO", f"Active Mosca planning horizon: Z={scenario_year}, X={x_lifetime}y, Y={y_migration}y")
    raw = []

    _log("INFO", "Executing source scanner (AST call-site visitor & regex fallback)...")
    src = _scan_source(directory)
    raw += src
    _log("INFO", f"Source scan complete: discovered {len(src)} cryptographic instances.")

    _log("INFO", "Executing dependency scanner (multi-manifest parser)...")
    deps = _scan_dependencies(directory)
    raw += deps
    _log("INFO", f"Dependency scan complete: discovered {len(deps)} cryptographic libraries.")

    _log("INFO", "Executing certificate scanner (X.509, PKCS#12, OpenSSH)...")
    certs = _scan_certificates(directory)
    raw += certs
    _log("INFO", f"Certificate scan complete: discovered {len(certs)} certificates & public keys.")

    _log("INFO", "Executing configuration scanner (cipher suites & protocols)...")
    cfgs = _scan_configs(directory)
    raw += cfgs
    _log("INFO", f"Configuration scan complete: discovered {len(cfgs)} configuration rules.")

    _log("INFO", "Executing binary constant pool scanner (JVM bytecode)...")
    bins = _scan_binaries(directory)
    raw += bins
    _log("INFO", f"Binary scan complete: discovered {len(bins)} compiled cryptographic references.")

    # Cross-scanner deduplication using deterministic identity
    _log("INFO", f"Deduplicating {len(raw)} raw cryptographic instances...")
    deduped = []
    seen = {}
    conf_rank = {"HIGH": 3, "MEDIUM": 2, "LOW": 1}
    for asset in raw:
        key = (
            os.path.normcase(os.path.abspath(asset.file_path)),
            asset.line_number,
            asset.algorithm.upper(),
            asset.usage.value
        )
        if key not in seen:
            seen[key] = asset
            deduped.append(asset)
        else:
            existing = seen[key]
            if conf_rank.get(asset.confidence, 0) > conf_rank.get(existing.confidence, 0) or (asset.key_size and not existing.key_size):
                idx = deduped.index(existing)
                deduped[idx] = asset
                seen[key] = asset
    _log("INFO", f"Deduplication complete: {len(deduped)} distinct cryptographic assets normalized.")

    _log("INFO", "Running Post-Quantum analysis pipeline (Quantum Rules, Mosca, Risk Scoring, PQC Recommendations)...")
    processed = []
    for asset in deduped:
        a = apply_quantum_rules(asset)
        a = compute_mosca(a, scenario_year, x_lifetime, y_migration)
        a = calculate_risk_score(a)
        a = generate_recommendations(a)
        processed.append(a)

    elapsed = time.time() - t0
    metrics = {
        "scan_time_s": round(elapsed, 3),
        "total_assets": len(processed),
        "quantum_vulnerable": sum(1 for a in processed if a.quantum_status.value == "Vulnerable"),
        "grover_weakened": sum(1 for a in processed if a.quantum_status.value == "Weakened"),
        "classically_broken": sum(1 for a in processed if a.quantum_status.value == "Legacy-broken"),
        "mosca_violations": sum(1 for a in processed if a.mosca_at_risk),
        "critical_risk": sum(1 for a in processed if a.risk_band == "Critical"),
        "high_risk": sum(1 for a in processed if a.risk_band == "High"),
        "medium_risk": sum(1 for a in processed if a.risk_band == "Medium"),
    }
    _log("SUCCESS", f"Scan pipeline complete: {len(processed)} assets analyzed in {metrics['scan_time_s']}s.")
    return processed, metrics
