"""
Automated regression test suite verifying backend hardening, controlled corpus precision,
and external repository manifest integrity.
"""
import os
import json
import pytest
from app.pipeline import run_full_scan
from app.scanners.source_scanner import scan_file
from app.scanners.config_scanner import scan_config_file
from app.cbom.cyclonedx import generate_cyclonedx_cbom, validate_cbom


def test_controlled_positive_corpus_precision():
    pos_dir = os.path.join(os.path.dirname(__file__), "controlled_corpus", "positive")
    assets, metrics = run_full_scan(pos_dir)
    assert len(assets) > 20
    # Verify critical algorithms are present
    algos = {a.algorithm.upper() for a in assets}
    assert "AES" in algos
    assert "RSA" in algos
    assert "ECDSA" in algos
    assert "SHA-256" in algos


def test_controlled_negative_corpus_zero_false_positives():
    neg_dir = os.path.join(os.path.dirname(__file__), "controlled_corpus", "negative")
    assets, metrics = run_full_scan(neg_dir)
    assert len(assets) == 0, f"Expected 0 findings in negative corpus, found {len(assets)}: {[a.algorithm for a in assets]}"


def test_json_test_metadata_not_scanned_as_source():
    expected_findings_path = os.path.join(os.path.dirname(__file__), "controlled_corpus", "expected_findings.json")
    findings = scan_file(expected_findings_path)
    assert len(findings) == 0, f"JSON metadata produced unexpected findings: {findings}"


def test_config_comment_before_and_after_ciphers():
    conf_content = """
    server {
        # Comment mentioning ciphers here
        ssl_protocols TLSv1.2 TLSv1.3;
        # Another comment before ssl_ciphers
        ssl_ciphers HIGH:!aNULL:!MD5;
    }
    """
    tmp_path = os.path.join(os.path.dirname(__file__), "temp_test_nginx.conf")
    with open(tmp_path, "w", encoding="utf-8") as f:
        f.write(conf_content)
    try:
        findings = scan_config_file(tmp_path)
        assert len(findings) > 0
        protos = [f.algorithm for f in findings]
        assert any("TLS" in p for p in protos)
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


def test_external_targets_manifest_integrity():
    manifest_path = os.path.join(os.path.dirname(__file__), "external_targets", "manifest.json")
    assert os.path.exists(manifest_path)
    with open(manifest_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert "repositories" in data
    assert len(data["repositories"]) == 3
    repo_names = {r["repository"] for r in data["repositories"]}
    assert repo_names == {"openssl", "cpython", "openssh"}
    for r in data["repositories"]:
        assert r["commit"]
        assert r["status"] == "PINNED"


def test_sha3_ast_visitor_detection():
    py_code = """
import hashlib

def run_hashes(val: bytes):
    # hashlib.sha3_256(b"in comment") should be ignored
    h224 = hashlib.sha3_224(val).hexdigest()
    h384 = hashlib.sha3_384(val).hexdigest()
    return h224, h384
"""
    tmp_path = os.path.join(os.path.dirname(__file__), "temp_test_sha3.py")
    with open(tmp_path, "w", encoding="utf-8") as f:
        f.write(py_code)
    try:
        findings = scan_file(tmp_path)
        assert len(findings) == 2
        for f in findings:
            assert f.algorithm == "SHA-3"
            assert f.rule_id == "ECDAT-SRC-SHA3-001"
            assert f.library == "hashlib"
        line_numbers = {f.line_number for f in findings}
        assert 6 in line_numbers
        assert 7 in line_numbers
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


def test_state_reset_restores_all_defaults():
    from backend.api.state import ECDATStateManager
    mgr = ECDATStateManager()
    mgr.scenario_year = 2050
    mgr.x_lifetime = 25.0
    mgr.y_migration = 7.0
    mgr.scan_path = "/custom/scanned/path"

    mgr.reset()

    assert mgr.scenario_year == 2035
    assert mgr.x_lifetime == 10.0
    assert mgr.y_migration == 3.0
    assert mgr.scan_path == ""
    assert mgr.assets == []
    assert mgr.current_stage == "IDLE"


def test_dashboard_status_completed_scan_zero_assets():
    from fastapi.testclient import TestClient
    from backend.api.main import app
    from backend.api.state import state

    client = TestClient(app)
    saved_path = state.scan_path
    saved_assets = list(state.assets)
    try:
        state.scan_path = "/clean/target/repo"
        state.assets = []
        resp = client.get("/api/dashboard")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "Complete"
        assert data["target_path"] == "/clean/target/repo"
        assert data["metrics"]["total_assets"] == 0
    finally:
        state.scan_path = saved_path
        state.assets = saved_assets

