"""
End-to-end verification of the complete ECDAT demo flow:
Scan -> Dashboard -> Inventory -> Finding -> Mosca -> Risk -> Migration -> CBOM -> Reports.
"""
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from backend.api.main import app

def main():
    c = TestClient(app)

    print("=== 1. SCAN ===")
    r = c.post("/api/scans", json={"use_corpus": True, "scenario_year": 2035})
    assert r.status_code == 200
    scan_res = r.json()
    print("Scan Status:", scan_res["current_stage"], "| Total assets:", scan_res["total_assets"])
    assert scan_res["total_assets"] == 25

    print("=== 2. DASHBOARD ===")
    r = c.get("/api/dashboard")
    assert r.status_code == 200
    dash = r.json()
    print("Total Assets:", dash["metrics"]["total_assets"])
    print("Quantum Exposure Distribution:", dash["quantum_exposure"])
    assert dash["quantum_exposure"]["QUANTUM_SAFE"] == 3
    assert dash["quantum_exposure"]["SHOR_BROKEN"] == 11
    assert dash["quantum_exposure"]["GROVER_WEAKENED"] == 5
    assert dash["quantum_exposure"]["CLASSICALLY_BROKEN"] == 6
    assert dash["metrics"]["mosca_violations"] == 16
    assert dash["cbom_status"]["valid"] is True

    print("=== 3. INVENTORY ===")
    r = c.get("/api/inventory?page=1&page_size=10")
    assert r.status_code == 200
    inv = r.json()
    print("Inventory total:", inv["total"], "| Page 1 count:", len(inv["items"]))
    assert inv["total"] == 25
    assert len(inv["items"]) == 10

    # Filter test
    r_filt = c.get("/api/inventory?threat=HNDL")
    assert r_filt.status_code == 200
    print("HNDL filtered count:", r_filt.json()["total"])
    assert r_filt.json()["total"] > 0

    print("=== 4. FINDING INSPECTION ===")
    r = c.get("/api/findings/0")
    assert r.status_code == 200
    f0 = r.json()
    print("Finding 0:", f0["rule_id"], "| Algo:", f0["algorithm"], "| Quantum:", f0["quantum_status"], "| Risk:", f0["risk_score"])
    assert f0["algorithm"]
    assert f0["line_number"] > 0

    print("=== 5. MOSCA SIMULATOR ===")
    r = c.get("/api/mosca")
    assert r.status_code == 200
    m0 = r.json()
    print("Mosca margin:", m0["security_margin"], "years | Violations:", m0["violations_count"], "| At Risk:", m0["at_risk"])
    assert m0["violations_count"] == 16

    # Simulate updated horizon
    r_sim = c.post("/api/mosca/simulate", json={"scenario_year": 2040, "x_lifetime": 5.0, "y_migration": 2.0, "recompute_scan": False})
    assert r_sim.status_code == 200
    m_sim = r_sim.json()
    print("Simulation (2040, X=5, Y=2) Security Margin:", m_sim["security_margin"], "| At risk:", m_sim["at_risk"])
    assert m_sim["security_margin"] == 7.0
    assert m_sim["at_risk"] is False

    # Restore scenario
    c.post("/api/mosca/simulate", json={"scenario_year": 2035, "x_lifetime": 10.0, "y_migration": 3.0, "recompute_scan": False})

    print("=== 6. RISK ANALYSIS ===")
    r = c.get("/api/risk")
    assert r.status_code == 200
    rk = r.json()
    print("Formula:", rk["formula"][:60], "...")
    print("Average Risk Score:", rk["average_score"], "| Top findings ranked:", len(rk["top_findings"]))
    assert len(rk["top_findings"]) > 0

    print("=== 7. MIGRATION GUIDANCE ===")
    r = c.get("/api/migration")
    assert r.status_code == 200
    mg = r.json()
    print("PQC Migration matrix items:", len(mg["matrix"]))
    print("Compliant count:", mg["summary"]["compliant_count"])
    assert mg["summary"]["compliant_count"] == 3
    assert "FIPS_203" in mg["standards"]
    assert "FIPS_204" in mg["standards"]

    print("=== 8. CYCLONEDX 1.6 CBOM ===")
    r = c.get("/api/cbom")
    assert r.status_code == 200
    cb = r.json()
    print("CBOM Component count:", cb["component_count"])
    print("CycloneDX 1.6 Schema Valid:", cb["validation"]["valid"], "| Schema Errors:", len(cb["validation"]["errors"]))
    assert cb["validation"]["valid"] is True
    assert len(cb["validation"]["errors"]) == 0
    assert cb["component_count"] == 25

    print("=== 9. REPORTS & DELIVERABLES ===")
    r = c.get("/api/reports")
    assert r.status_code == 200
    rep = r.json()
    print("Total Deliverables Available:", rep["total_deliverables"])
    assert rep["total_deliverables"] == 6

    for fmt in ["json", "csv", "sarif", "html", "pdf", "md"]:
        dl = c.get(f"/api/reports/download/{fmt}")
        assert dl.status_code == 200
        print(f"  -> Download {fmt.upper()} verified: {len(dl.content):,} bytes")
        assert len(dl.content) > 50

    print("\n[SUCCESS] Entire 9-stage demo flow verified end-to-end with ZERO errors!")

if __name__ == "__main__":
    main()
