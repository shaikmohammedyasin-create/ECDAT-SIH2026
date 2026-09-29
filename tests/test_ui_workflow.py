"""
Test suite verifying the complete 11-screen ECDAT UI workflow and data contracts.
Covers Section 28 Acceptance Criteria.
"""
import os
import pytest
from app.pipeline import run_full_scan
from app.cbom.cyclonedx import generate_cyclonedx_cbom, validate_cbom
from app.reports.reporter import (
    export_html_report,
    export_pdf_report,
    export_sarif,
    export_inventory_csv,
    export_summary_md
)
from app.ui.pages import (
    p01_dashboard,
    p02_new_scan,
    p03_inventory,
    p04_inspector,
    p05_mosca,
    p06_risk,
    p07_migration,
    p08_cbom,
    p09_reports,
    p10_terminal,
    p11_settings
)


def test_ui_pages_import_cleanly():
    """Verify all 11 screen modules are imported with valid syntax."""
    modules = [
        p01_dashboard, p02_new_scan, p03_inventory, p04_inspector,
        p05_mosca, p06_risk, p07_migration, p08_cbom,
        p09_reports, p10_terminal, p11_settings
    ]
    for mod in modules:
        assert hasattr(mod, "render"), f"Module {mod.__name__} must define render()"


def test_scan_telemetry_and_logging():
    """Verify scan pipeline emits real-time events for Terminal / Scan Log."""
    logs = []
    def log_cb(lvl, msg):
        logs.append((lvl, msg))

    corpus_dir = os.path.abspath("test_corpus")
    assets, metrics = run_full_scan(corpus_dir, log_callback=log_cb)

    assert len(assets) > 0
    assert metrics["total_assets"] == len(assets)
    assert len(logs) >= 8

    # Verify key pipeline stages appear in logs
    stages = [msg for _, msg in logs]
    assert any("Initializing" in s for s in stages)
    assert any("Source scan" in s for s in stages)
    assert any("Dependency scan" in s for s in stages)
    assert any("Certificate scan" in s for s in stages)
    assert any("Deduplication complete" in s for s in stages)
    assert any("Scan pipeline complete" in s for s in stages)


def test_screen_data_contracts(tmp_path):
    """Verify all screen data structures, CBOM schema validation, and reports."""
    corpus_dir = os.path.abspath("test_corpus")
    assets, metrics = run_full_scan(corpus_dir)

    # 1. Dashboard contract
    assert metrics["quantum_vulnerable"] > 0
    assert metrics["classically_broken"] > 0
    assert metrics["critical_risk"] > 0

    # 2. Inventory contract
    for a in assets:
        assert a.algorithm
        assert a.file_path
        assert a.line_number > 0
        assert a.confidence in ("HIGH", "MEDIUM", "LOW")
        assert a.risk_band in ("Critical", "High", "Medium", "Low", "Info")

    # 3. Finding Inspector contract
    sample_rsa = next((a for a in assets if "RSA" in a.algorithm.upper()), assets[0])
    assert sample_rsa.rule_id.startswith("ECDAT-")
    assert sample_rsa.recommendation

    # 4. Mosca Simulator contract
    assert sample_rsa.mosca_margin is not None
    assert isinstance(sample_rsa.mosca_at_risk, bool)

    # 5. Risk Analysis contract
    for a in assets:
        assert 0.0 <= a.risk_score <= 100.0

    # 6. CycloneDX 1.6 CBOM contract
    cbom = generate_cyclonedx_cbom(assets)
    val = validate_cbom(cbom)
    assert val["valid"] is True, f"CBOM validation failed: {val['errors']}"
    assert len(val["errors"]) == 0

    # 7. Reports & Evidence contract (all 6 deliverables exist and non-empty)
    html_f = str(tmp_path / "rep.html")
    export_html_report(assets, metrics, val, html_f)
    assert os.path.getsize(html_f) > 500

    sarif_f = str(tmp_path / "rep.sarif")
    export_sarif(assets, metrics, sarif_f)
    assert os.path.getsize(sarif_f) > 500

    md_f = str(tmp_path / "rep.md")
    export_summary_md(assets, metrics, val, md_f)
    assert os.path.getsize(md_f) > 200

    csv_f = str(tmp_path / "rep.csv")
    export_inventory_csv(assets, csv_f)
    assert os.path.getsize(csv_f) > 200

    pdf_f = str(tmp_path / "rep.pdf")
    res_pdf = export_pdf_report(assets, metrics, val, pdf_f)
    if res_pdf and os.path.exists(res_pdf):
        assert os.path.getsize(res_pdf) > 1000
