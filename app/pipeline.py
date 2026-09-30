"""
End-to-end ECDAT scan pipeline - Performance Optimized.
Single-pass walk, O(1) dedup, parallel analysis via ThreadPoolExecutor.
"""
import os
import time
from typing import List, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

from app.models.crypto_asset import CryptoAsset
from app.scanners.source_scanner import scan_file
from app.scanners.dependency_scanner import scan_dependency_file
from app.scanners.certificate_scanner import scan_certificate_file
from app.scanners.config_scanner import scan_config_file
from app.scanners.binary_scanner import scan_binary_file
from app.analysis.quantum_rules import apply_quantum_rules
from app.analysis.mosca import compute_mosca
from app.analysis.risk import calculate_risk_score
from app.analysis.recommendations import generate_recommendations

DEP_FILENAMES = {
    "requirements.txt", "requirements-dev.txt", "pom.xml",
    "package.json", "package-lock.json", "pyproject.toml",
    "go.mod", "cargo.toml", "build.gradle"
}
CERT_EXTS = (".pem", ".crt", ".cer", ".der", ".p12", ".pfx", ".pub")
CONFIG_EXTS = (".conf", ".cfg")
CONFIG_NAMES = {"nginx.conf", "sshd_config", "openssl.cnf", "Dockerfile"}
BINARY_EXTS = (".class", ".jar", ".war")
SOURCE_EXTS = (".py", ".js", ".java", ".ts", ".jsx", ".tsx", ".c", ".h", ".cpp", ".cc")
PRUNE_DIRS = {
    ".git", "node_modules", "venv", "__pycache__", ".pytest_cache",
    ".hg", ".svn", "build", "dist", "target", ".idea", ".gradle",
    ".tox", "htmlcov", ".eggs",
}

MAX_ASSETS_PER_SCAN = 2000
_WORKERS = min(8, (os.cpu_count() or 4))


def _analyse_asset(asset, scenario_year, x_lifetime, y_migration):
    a = apply_quantum_rules(asset)
    a = compute_mosca(a, scenario_year, x_lifetime, y_migration)
    a = calculate_risk_score(a)
    a = generate_recommendations(a)
    return a


def run_full_scan(
    directory: str,
    scenario_year: int = 2035,
    x_lifetime: float = 10.0,
    y_migration: float = 3.0,
    log_callback=None,
) -> Tuple[List[CryptoAsset], dict]:
    def _log(level, msg):
        if log_callback:
            log_callback(level, msg)

    t0 = time.time()
    _log("INFO", f"ECDAT engine starting. Target: {directory}")
    _log("INFO", f"Mosca: Z={scenario_year}, X={x_lifetime}y, Y={y_migration}y | Workers: {_WORKERS}")

    src, deps, certs, cfgs, bins = [], [], [], [], []

    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if d not in PRUNE_DIRS]
        for f in files:
            fp = os.path.join(root, f)
            fl = f.lower()
            if fl in DEP_FILENAMES:
                deps.extend(scan_dependency_file(fp))
            elif fl.endswith(CERT_EXTS) or ".crt" in fl:
                certs.extend(scan_certificate_file(fp))
            elif fl.endswith(CONFIG_EXTS) or fl in CONFIG_NAMES or "tls" in fl:
                cfgs.extend(scan_config_file(fp))
            elif fl.endswith(BINARY_EXTS):
                bins.extend(scan_binary_file(fp))
            elif fl.endswith(SOURCE_EXTS):
                src.extend(scan_file(fp))

    raw = src + deps + certs + cfgs + bins
    _log("INFO", f"Discovery: {len(src)} src, {len(deps)} deps, {len(certs)} certs, {len(cfgs)} cfg, {len(bins)} bin.")

    # O(1) deduplication
    _log("INFO", f"Deduplicating {len(raw)} raw instances...")
    deduped: List[CryptoAsset] = []
    seen = {}
    conf_rank = {"HIGH": 3, "MEDIUM": 2, "LOW": 1}
    for asset in raw:
        key = (
            os.path.normcase(os.path.abspath(asset.file_path)),
            asset.line_number,
            asset.algorithm.upper(),
            asset.usage.value,
        )
        if key not in seen:
            seen[key] = len(deduped)
            deduped.append(asset)
        else:
            idx = seen[key]
            existing = deduped[idx]
            if (
                conf_rank.get(asset.confidence, 0) > conf_rank.get(existing.confidence, 0)
                or (asset.key_size and not existing.key_size)
            ):
                deduped[idx] = asset

    total_discovered = len(deduped)
    _log("INFO", f"Dedup done: {total_discovered} distinct assets.")

    if total_discovered > MAX_ASSETS_PER_SCAN:
        _log("WARN", f"Large repo: cap={MAX_ASSETS_PER_SCAN}, discovered={total_discovered}.")
        deduped = deduped[:MAX_ASSETS_PER_SCAN]

    # Parallel PQ analysis
    _log("INFO", f"Parallel analysis: {len(deduped)} assets, {_WORKERS} threads...")
    processed: List[CryptoAsset] = [None] * len(deduped)  # type: ignore

    with ThreadPoolExecutor(max_workers=_WORKERS) as executor:
        futures = {
            executor.submit(_analyse_asset, asset, scenario_year, x_lifetime, y_migration): i
            for i, asset in enumerate(deduped)
        }
        for future in as_completed(futures):
            idx = futures[future]
            try:
                processed[idx] = future.result()
            except Exception as exc:
                processed[idx] = deduped[idx]
                _log("WARN", f"Asset {idx} analysis error: {exc}")

    ok = [a for a in processed if a is not None]
    elapsed = time.time() - t0
    metrics = {
        "scan_time_s": round(elapsed, 3),
        "total_assets": total_discovered,
        "analyzed_assets": len(ok),
        "quantum_vulnerable": sum(1 for a in ok if a.quantum_status.value == "Vulnerable"),
        "grover_weakened": sum(1 for a in ok if a.quantum_status.value == "Weakened"),
        "classically_broken": sum(1 for a in ok if a.quantum_status.value == "Legacy-broken"),
        "mosca_violations": sum(1 for a in ok if a.mosca_at_risk),
        "critical_risk": sum(1 for a in ok if a.risk_band == "Critical"),
        "high_risk": sum(1 for a in ok if a.risk_band == "High"),
        "medium_risk": sum(1 for a in ok if a.risk_band == "Medium"),
        "capped": total_discovered > MAX_ASSETS_PER_SCAN,
    }
    _log("SUCCESS", f"Pipeline done: {len(ok)} assets in {elapsed:.2f}s.")
    return ok, metrics
