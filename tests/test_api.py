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
