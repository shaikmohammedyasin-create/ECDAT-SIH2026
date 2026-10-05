"""
Test suite verifying all FastAPI backend endpoints for ECDAT Security Workstation.
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from fastapi.testclient import TestClient
from backend.api.main import app

client = TestClient(app)


def test_health_check():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "healthy"


def test_dashboard_endpoint():
    resp = client.get("/api/dashboard")
    assert resp.status_code == 200
    data = resp.json()
    assert "metrics" in data
    assert data["metrics"]["total_assets"] > 0
    assert "risk_distribution" in data
    assert "quantum_exposure" in data
    assert "recent_findings" in data
    assert len(data["recent_findings"]) > 0
    assert data["cbom_status"]["valid"] is True


def test_inventory_endpoint():
    resp = client.get("/api/inventory?page=1&page_size=20")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] > 0
    assert len(data["items"]) > 0

    # Test filtering
    filtered_resp = client.get("/api/inventory?threat=HNDL")
    assert filtered_resp.status_code == 200
    for item in filtered_resp.json()["items"]:
        assert item["threat"] == "HNDL"


def test_finding_detail_endpoint():
    resp = client.get("/api/findings/0")
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == 0
    assert data["algorithm"]
    assert data["file_path"]
    assert data["line_number"] > 0
    assert data["rule_id"].startswith("ECDAT-")


def test_mosca_endpoint():
    resp = client.get("/api/mosca")
    assert resp.status_code == 200
    data = resp.json()
    assert "scenario_year" in data
    assert "security_margin" in data

    # Test simulation post
    sim_resp = client.post("/api/mosca/simulate", json={
        "scenario_year": 2040,
        "x_lifetime": 15.0,
        "y_migration": 5.0,
        "recompute_scan": False
    })
    assert sim_resp.status_code == 200
    sim_data = sim_resp.json()
    assert sim_data["scenario_year"] == 2040


def test_risk_analysis_endpoint():
    resp = client.get("/api/risk")
    assert resp.status_code == 200
    data = resp.json()
    assert "formula" in data
    assert "weights" in data
    assert "average_score" in data
    assert len(data["top_findings"]) > 0


def test_migration_guidance_endpoint():
    resp = client.get("/api/migration")
    assert resp.status_code == 200
    data = resp.json()
    assert "matrix" in data
    assert len(data["matrix"]) > 0
    assert "standards" in data


def test_cbom_endpoint():
    resp = client.get("/api/cbom")
    assert resp.status_code == 200
    data = resp.json()
    assert data["validation"]["valid"] is True
    assert len(data["validation"]["errors"]) == 0
    assert data["component_count"] > 0

    dl_resp = client.get("/api/cbom/download")
    assert dl_resp.status_code == 200
    assert "attachment" in dl_resp.headers["content-disposition"]


def test_reports_and_downloads_endpoint():
    resp = client.get("/api/reports")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_deliverables"] == 6

    # Test downloads for all 6 formats
    for fmt in ["json", "csv", "sarif", "html", "pdf", "md"]:
        dl = client.get(f"/api/reports/download/{fmt}")
        assert dl.status_code == 200, f"Download failed for {fmt}"
        assert len(dl.content) > 50, f"Empty content for {fmt}"


def test_terminal_endpoint():
    resp = client.get("/api/terminal")
    assert resp.status_code == 200
    logs = resp.json()
    assert isinstance(logs, list)
    assert len(logs) > 0


def test_settings_endpoint():
    resp = client.get("/api/settings")
    assert resp.status_code == 200
    data = resp.json()
    assert data["air_gap_enforced"] is True
    assert data["zero_key_persistence"] is True


def test_scan_endpoints_and_readiness():
    # 1. Trigger scan via POST /api/scans
    post_resp = client.post("/api/scans", json={"use_corpus": True, "scenario_year": 2035})
    assert post_resp.status_code == 200
    scan_info = post_resp.json()
    assert "scan_id" in scan_info
    scan_id = scan_info["scan_id"]
    assert scan_info["total_assets"] > 0

    # 2. GET /api/scans/status
    st_resp = client.get("/api/scans/status")
    assert st_resp.status_code == 200
    assert st_resp.json()["scan_id"] == scan_id

    # 3. GET /api/scans/{id}
    id_resp = client.get(f"/api/scans/{scan_id}")
    assert id_resp.status_code == 200
    assert id_resp.json()["total_assets"] > 0

    # 4. GET /api/scans/{id}/findings
    f_resp = client.get(f"/api/scans/{scan_id}/findings")
    assert f_resp.status_code == 200
    assert f_resp.json()["total"] > 0

    # 5. GET /api/scans/{id}/inventory
    inv_resp = client.get(f"/api/scans/{scan_id}/inventory")
    assert inv_resp.status_code == 200
    assert inv_resp.json()["total"] > 0

    # 6. GET /api/scans/{id}/risk
    r_resp = client.get(f"/api/scans/{scan_id}/risk")
    assert r_resp.status_code == 200
    assert "formula" in r_resp.json()

    # 7. GET /api/scans/{id}/mosca
    m_resp = client.get(f"/api/scans/{scan_id}/mosca")
    assert m_resp.status_code == 200
    assert "scenario_year" in m_resp.json()

    # 8. GET /api/scans/{id}/migration
    mig_resp = client.get(f"/api/scans/{scan_id}/migration")
    assert mig_resp.status_code == 200
    assert len(mig_resp.json()["matrix"]) > 0

    # 9. GET /api/scans/{id}/cbom
    cbom_resp = client.get(f"/api/scans/{scan_id}/cbom")
    assert cbom_resp.status_code == 200
    assert cbom_resp.json()["validation"]["valid"] is True

    # 10. GET /api/scans/{id}/reports
    rep_resp = client.get(f"/api/scans/{scan_id}/reports")
    assert rep_resp.status_code == 200
    assert rep_resp.json()["total_deliverables"] == 6


def test_path_traversal_protection():
    # Attempting path traversal with '..' is rejected with 400 Bad Request
    resp = client.post("/api/scans", json={"use_corpus": False, "path": "../../../some_folder"})
    assert resp.status_code == 400

    # Non-existent path without traversal returns 404 Not Found
    resp_404 = client.post("/api/scans", json={"use_corpus": False, "path": "non_existent_folder_xyz_999"})
    assert resp_404.status_code == 404

    # Attempting to scan system root is rejected with 400 Bad Request
    system_path = r"C:\Windows" if os.name == "nt" else "/etc"
    resp_root = client.post("/api/scans", json={"use_corpus": False, "path": system_path})
    assert resp_root.status_code == 400


def test_paste_scan_endpoint():
    resp = client.post(
        "/api/scans/paste",
        data={
            "code": "import hashlib\nh = hashlib.sha256().hexdigest()",
            "filename": "crypto_snippet.py",
            "scenario_year": "2035",
            "x_lifetime": "10.0",
            "y_migration": "3.0"
        }
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["scan_in_progress"] is False
    assert data["current_stage"] == "COMPLETE"
    assert data["total_assets"] >= 1
    assert "quantum_safe" in data["metrics"]


def test_upload_scan_endpoint():
    import io
    import zipfile
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("sample.py", "import hashlib\nh = hashlib.md5().hexdigest()")
    buf.seek(0)

    resp = client.post(
        "/api/scans/upload",
        files={"file": ("project.zip", buf.getvalue(), "application/zip")},
        data={"scenario_year": "2035", "x_lifetime": "10.0", "y_migration": "3.0"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["scan_in_progress"] is False
    assert data["current_stage"] == "COMPLETE"
    assert data["total_assets"] >= 1
    assert data["metrics"]["classically_broken"] >= 1

    # Reset state back to default controlled corpus
    reset_resp = client.post("/api/scans", json={"use_corpus": True, "scenario_year": 2035})
    assert reset_resp.status_code == 200
    assert reset_resp.json()["total_assets"] == 25


