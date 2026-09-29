"""
ECDAT Streamlit dashboard — multi-page UI (source-of-truth §22).

    Dashboard  ·  New Scan  ·  Inventory  ·  Asset Detail  ·  Mosca Simulator  ·  Reports

Runs the full ECDAT pipeline over a local folder and visualises:
total/quantum-vulnerable/classically-broken assets, Mosca X+Y>Z, 0-100 risk,
deterministic PQC/hybrid recommendations, and a validated CycloneDX 1.6 CBOM.

Launch:  python run.py   (or:  streamlit run app/ui/dashboard.py)
"""
import os
import json
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import streamlit as st
import pandas as pd
import plotly.express as px

from app.pipeline import run_full_scan
from app.cbom.cyclonedx import generate_cyclonedx_cbom, validate_cbom
from app.reports.reporter import export_html_report, export_pdf_report, export_sarif, export_inventory_csv, export_summary_md

st.set_page_config(page_title="ECDAT — Cryptographic Discovery & Analysis Tool",
                   layout="wide", page_icon="🛡️")

# Enterprise cybersecurity dark palette styling
st.markdown("""
<style>
    .metric-card {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 12px;
    }
    .badge-critical { background-color: #991b1b; color: white; padding: 2px 8px; border-radius: 4px; font-weight: bold; }
    .badge-high { background-color: #c2410c; color: white; padding: 2px 8px; border-radius: 4px; font-weight: bold; }
    .badge-med { background-color: #b45309; color: white; padding: 2px 8px; border-radius: 4px; font-weight: bold; }
    .badge-low { background-color: #15803d; color: white; padding: 2px 8px; border-radius: 4px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

CURRENT_YEAR = 2026
DEFAULT_PATH = os.path.abspath("test_corpus")

# ------------------------------------------------------------------ state init
def _state(key, default):
    if key not in st.session_state:
        st.session_state[key] = default


_state("assets", None)
_state("metrics", None)
_state("scan_path", DEFAULT_PATH)
_state("scenario_year", 2035)
_state("x_lifetime", 10.0)
_state("y_migration", 3.0)


def run_scan(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Path does not exist: {path}")
    assets, metrics = run_full_scan(
        path,
        scenario_year=st.session_state["scenario_year"],
        x_lifetime=st.session_state["x_lifetime"],
        y_migration=st.session_state["y_migration"],
    )
    st.session_state["assets"] = assets
    st.session_state["metrics"] = metrics
    return assets, metrics


def _assets():
    return st.session_state["assets"] or []


def _as_df():
    assets = _assets()
    return pd.DataFrame([{
        "algorithm": a.algorithm,
        "key_size": a.key_size or "N/A",
        "mode": a.mode or "N/A",
        "type": a.asset_type.value,
        "usage": a.usage.value,
        "quantum": a.quantum_status.value,
        "threat": "HNDL" if a.hndl_risk else ("TNFL" if a.tnfl_risk else "None"),
        "risk_score": a.risk_score,
        "risk_band": a.risk_band,
        "mosca_margin": round(a.mosca_margin, 1) if a.mosca_margin is not None else "N/A",
        "rule_id": a.rule_id or "N/A",
        "confidence": a.confidence,
        "exposure": a.exposure,
        "file": os.path.basename(a.file_path),
        "line": a.line_number,
        "recommendation": a.recommendation or "",
        "file_path": a.file_path,
    } for a in assets])


# ------------------------------------------------------------------ sidebar
with st.sidebar:
    st.title("🛡️ ECDAT")
    st.caption("Enterprise Cryptographic Discovery & Analysis Tool")
    st.caption("NTRO · Problem Statement 26164 · Post-Quantum Cryptography Readiness")
    st.markdown("---")
    page = st.radio("Navigation", [
        "Dashboard", "New Scan", "Inventory",
        "Asset Detail", "Mosca Simulator", "Reports",
    ])
    st.markdown("---")
    st.markdown("**Mosca Scenario (Planning Horizon)**")
    st.caption("⚠️ These are planning scenarios, NOT predictions of a CRQC arrival date.")
    st.session_state["scenario_year"] = st.selectbox(
        "CRQC scenario year (Z)", [2030, 2035, 2040],
        index=[2030, 2035, 2040].index(st.session_state["scenario_year"]),
    )
    st.session_state["x_lifetime"] = st.slider("Data / Trust lifetime X (yrs)",
                                               1.0, 30.0, st.session_state["x_lifetime"], 0.5)
    st.session_state["y_migration"] = st.slider("Migration time Y (yrs)",
                                                0.5, 10.0, st.session_state["y_migration"], 0.5)


# ===================================================================
# DASHBOARD
# ===================================================================
def page_dashboard():
    st.header("Executive Cryptographic Risk Dashboard")
    st.caption("Continuous Quantum Vulnerability & Post-Quantum Cryptography Migration Status")
    assets = _assets()
    if not assets:
        st.info("ℹ️ No scan loaded yet. Go to **New Scan** to run discovery on your project or the controlled corpus.")
        return
    m = st.session_state["metrics"]
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Crypto Assets", m["total_assets"])
    c2.metric("Shor Vulnerable", m["quantum_vulnerable"], delta_color="inverse")
    c3.metric("Classically Broken", m["classically_broken"], delta_color="inverse")
    c4.metric("Mosca Violations (X+Y>Z)", m["mosca_violations"], delta_color="inverse")
    c5.metric("Critical Risk", m["critical_risk"], delta_color="inverse")

    st.markdown("---")
    colA, colB = st.columns(2)
    with colA:
        st.subheader("Risk Distribution by Band")
        df = _as_df()
        band_counts = df["risk_band"].value_counts().reindex(
            ["Critical", "High", "Medium", "Low", "Info"], fill_value=0)
        fig = px.bar(band_counts, orientation="h", color=band_counts.index,
                     color_discrete_map={
                         "Critical": "#dc2626", "High": "#ea580c", "Medium": "#d97706",
                         "Low": "#16a34a", "Info": "#64748b"})
        fig.update_layout(showlegend=False, height=320, margin=dict(l=0, r=0, t=10, b=0),
                          xaxis_title="Number of Assets", yaxis_title="Risk Band")
        st.plotly_chart(fig, use_container_width=True)
    with colB:
        st.subheader("Top Priority Cryptographic Assets")
        top = df.sort_values("risk_score", ascending=False).head(8)
        for _, r in top.iterrows():
            threat_badge = f" · `{r['threat']}`" if r['threat'] != "None" else ""
            st.markdown(
                f"**[{r['risk_band'].upper()}]** `{r['algorithm']}` ({r['usage']}){threat_badge} — "
                f"Score: **{r['risk_score']:.1f}** · `{r['file']}:{r['line']}`"
            )
    st.caption(f"⚡ Scan Time: {m['scan_time_s']}s · Active Target: `{st.session_state['scan_path']}`")


# ===================================================================
# NEW SCAN
# ===================================================================
def page_new_scan():
    st.header("New Scan")
    st.caption("Scan a local project/repository. All analysis is air-gapped — source never leaves this machine.")
    path = st.text_input("Target repository / directory path", st.session_state["scan_path"])
    st.session_state["scan_path"] = path

    use_corpus = st.checkbox("Use bundled controlled corpus (recommended for demo)",
                             value=("test_corpus" in path))
    if use_corpus:
        path = os.path.join(os.getcwd(), "test_corpus")
        st.caption(f"Will scan: `{path}`")

    if st.button("🚀 Start Cryptographic Scan", type="primary"):
        with st.spinner("Discovering crypto, classifying quantum risk, computing Mosca..."):
            try:
                assets, metrics = run_scan(path if not use_corpus else path)
                st.success(f"Scan complete: {metrics['total_assets']} assets in {metrics['scan_time_s']}s")
            except Exception as e:
                st.error(f"Scan failed: {e}")
        st.rerun()

    if _assets():
        st.markdown("---")
        st.subheader("Latest scan summary")
        m = st.session_state["metrics"]
        st.json(m)


# ===================================================================
# INVENTORY
# ===================================================================
# ===================================================================
# INVENTORY
# ===================================================================
def page_inventory():
    st.header("Cryptographic Asset Inventory")
    st.caption("Normalized Bill of Cryptographic Materials (CBOM) with Quantum Risk Classification")
    df = _as_df()
    if df.empty:
        st.info("ℹ️ No assets yet. Run a scan from the **New Scan** page first.")
        return

    # Filter Bar
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        algo_filter = st.selectbox("Algorithm", ["All"] + sorted(df["algorithm"].unique()))
    with c2:
        q_filter = st.selectbox("Quantum Status", ["All"] + sorted(df["quantum"].unique()))
    with c3:
        threat_filter = st.selectbox("Threat Flag", ["All", "HNDL", "TNFL"])
    with c4:
        band_filter = st.selectbox("Risk Band", ["All", "Critical", "High", "Medium", "Low", "Info"])

    f = df.copy()
    if algo_filter != "All":
        f = f[f["algorithm"] == algo_filter]
    if q_filter != "All":
        f = f[f["quantum"] == q_filter]
    if threat_filter != "All":
        f = f[f["threat"] == threat_filter]
    if band_filter != "All":
        f = f[f["risk_band"] == band_filter]

    def color_risk(v):
        return {
            "Critical": "#991b1b",
            "High": "#c2410c",
            "Medium": "#b45309",
            "Low": "#15803d",
            "Info": "#475569"
        }.get(v, "#334155")

    # Reorder columns for optimal readability
    display_cols = [
        "rule_id", "algorithm", "key_size", "mode", "type", "usage",
        "quantum", "threat", "risk_score", "risk_band", "mosca_margin",
        "confidence", "file", "line"
    ]
    styled = f[display_cols].style.map(lambda v: f"background-color: {color_risk(v)}; color: white; font-weight: bold;", subset=["risk_band"])
    st.dataframe(styled, use_container_width=True, hide_index=True)
    st.caption(f"Displaying **{len(f)}** of **{len(df)}** discovered assets")


# ===================================================================
# ASSET DETAIL
# ===================================================================
def page_asset_detail():
    st.header("Asset Detail — Deep Forensic Evidence & Migration Plan")
    assets = _assets()
    if not assets:
        st.info("ℹ️ No assets yet. Run a scan from the **New Scan** page first.")
        return

    options = {
        i: f"[{a.risk_score:.1f} | {a.risk_band.upper()}] {a.algorithm}{'-' + str(a.key_size) if a.key_size else ''} "
           f"({a.usage.value}) — {os.path.basename(a.file_path)}:{a.line_number}"
        for i, a in enumerate(assets)
    }
    sel = st.selectbox("Select Cryptographic Asset to Inspect", list(options.keys()), format_func=lambda i: options[i])
    a = assets[sel]

    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("📍 Forensic Evidence & Provenance")
        st.markdown(f"**Rule ID:** `{a.rule_id or 'N/A'}` · **Confidence:** `{a.confidence}`")
        st.markdown(f"**Source Location:** `{a.file_path}:{a.line_number}`")
        st.code(a.source_snippet, language="python" if a.file_path.endswith(".py") else "text")

        st.markdown(f"**Asset Type:** `{a.asset_type.value}` · **Primitive:** `{a.primitive}`")
        st.markdown(f"**Parameters:** Key Size: `{a.key_size or 'N/A'}` · Mode: `{a.mode or 'N/A'}` · Padding: `{a.padding or 'N/A'}`")
        st.markdown(f"**Quantum Vulnerability Class:** `{a.quantum_vuln_class.value}` (`{a.quantum_status.value}`)")
        
        threat_desc = []
        if a.hndl_risk:
            threat_desc.append("🚨 **HNDL (Harvest Now, Decrypt Later):** Data can be intercepted now and decrypted once a CRQC arrives.")
        if a.tnfl_risk:
            threat_desc.append("🚨 **TNFL (Trust Now, Forge Later):** Public key signatures can be forged, invalidating long-lived trust.")
        if not threat_desc:
            threat_desc.append("✅ No immediate HNDL/TNFL exposure detected.")
        st.markdown("\n".join(threat_desc))

    with c2:
        st.subheader("⏳ Mosca Analysis (X + Y > Z)")
        x = st.session_state["x_lifetime"]
        y = st.session_state["y_migration"]
        z = st.session_state["scenario_year"] - CURRENT_YEAR
        margin = a.mosca_margin
        
        st.markdown(f"""
        - **Data / Trust Lifetime (X):** `{x} years`
        - **Migration Time Required (Y):** `{y} years`
        - **CRQC Horizon (Z = {st.session_state['scenario_year']} − {CURRENT_YEAR}):** `{z} years`
        - **Combined Exposure (X + Y):** `{round(x + y, 1)} years`
        - **Mosca Margin [Z − (X + Y)]:** `{round(margin, 1) if margin is not None else 'N/A'} years`
        """)
        
        if a.mosca_at_risk:
            st.error(f"🚨 **CRQC VULNERABLE:** X + Y ({round(x+y, 1)} yr) > Z ({z} yr). Cryptographic transition must start immediately.")
        else:
            st.success(f"✅ **SAFE FOR SCENARIO {st.session_state['scenario_year']}:** Positive margin ({round(margin, 1) if margin is not None else 0} yr).")

        st.markdown("---")
        st.markdown(f"### Priority Risk Score: **{a.risk_score:.1f} / 100** (`{a.risk_band.upper()}`)")
        if a.hygiene_critical:
            st.warning("⚠️ **Hygiene-Critical:** Classically broken algorithm requires remediation independent of quantum risk.")

    st.markdown("---")
    st.subheader("🛡️ PQC & Hybrid Migration Recommendation")
    st.info(f"**Primary Action:** {a.recommendation}")
    if a.why_risky:
        st.markdown(f"**Risk Rationale:** {a.why_risky}")
    
    col_rec1, col_rec2 = st.columns(2)
    with col_rec1:
        st.markdown(f"**Hybrid Transition Group:** `{a.hybrid_option or 'None (Direct Migration)'}`")
        st.markdown(f"**Standard Reference:** `{a.standard or 'NIST Post-Quantum Cryptography'}`")
    with col_rec2:
        st.markdown(f"**Migration Effort:** `{a.migration_effort or 'Moderate'}`")
    
    if a.migration_path:
        st.markdown("**Deterministic Migration Steps:**")
        for step in a.migration_path:
            st.markdown(f"- {step}")


# ===================================================================
# MOSCA SIMULATOR
# ===================================================================
def page_mosca():
    st.header("Interactive Mosca Inequality Simulator (X + Y > Z)")
    st.caption("Evaluate quantum risk horizons across Aggressive, Baseline, and Conservative planning scenarios.")
    
    c1, c2, c3 = st.columns(3)
    sy = c1.number_input("CRQC Scenario Year (Z)", 2026, 2060, st.session_state["scenario_year"])
    x = c2.number_input("X: Security / Trust Lifetime (years)", 0.0, 50.0, st.session_state["x_lifetime"], 0.5)
    y = c3.number_input("Y: Migration & Deployment Time (years)", 0.0, 20.0, st.session_state["y_migration"], 0.5)
    
    z = sy - CURRENT_YEAR
    margin = z - (x + y)
    at_risk = margin < 0

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Required Protection (X + Y)", f"{round(x + y, 1)} yr")
    m2.metric("CRQC Horizon (Z)", f"{z} yr")
    m3.metric("Security Margin [Z − (X+Y)]", f"{round(margin, 1)} yr", delta=round(margin, 1))
    m4.metric("Risk Status", "🚨 AT RISK" if at_risk else "✅ SECURE", delta_color="inverse" if at_risk else "normal")

    st.markdown("---")
    st.subheader("Dynamic Model Re-computation")
    st.markdown("Recompute all inventory risk scores with the above parameters:")
    if st.button("Apply Parameters to Active Scan", type="primary"):
        st.session_state["scenario_year"] = sy
        st.session_state["x_lifetime"] = x
        st.session_state["y_migration"] = y
        run_scan(st.session_state["scan_path"])
        st.success("Re-computed complete inventory risk scores with updated parameters.")
        st.rerun()


# ===================================================================
# REPORTS
# ===================================================================
def page_reports():
    st.header("Reports & Cryptographic Bill of Materials (CBOM)")
    st.caption("Standardized CycloneDX 1.6 CBOM Export and Schema Validation")
    assets = _assets()
    if not assets:
        st.info("ℹ️ No assets available. Run a scan from the **New Scan** page first.")
        return

    cbom = generate_cyclonedx_cbom(assets)
    validation = validate_cbom(cbom)

    u1, u2, u3 = st.columns(3)
    u1.metric("Specification Format", "CycloneDX 1.6")
    u2.metric("CBOM Components", len(cbom["components"]))
    u3.metric("Official Schema Validation",
              "PASS ✓ (0 Errors)" if validation["valid"] else "FAIL",
              delta_color="normal" if validation["valid"] else "inverse")

    st.markdown("---")
    st.subheader("Download Deliverables")
    metrics = st.session_state.get("metrics") or {}

    import tempfile
    with tempfile.TemporaryDirectory() as tmp_dir:
        html_p = os.path.join(tmp_dir, "report.html")
        export_html_report(assets, metrics, validation, html_p)
        with open(html_p, "r", encoding="utf-8") as f:
            html_bytes = f.read()

        sarif_p = os.path.join(tmp_dir, "findings.sarif")
        export_sarif(assets, metrics, sarif_p)
        with open(sarif_p, "r", encoding="utf-8") as f:
            sarif_bytes = f.read()

        md_p = os.path.join(tmp_dir, "summary.md")
        export_summary_md(assets, metrics, validation, md_p)
        with open(md_p, "r", encoding="utf-8") as f:
            md_bytes = f.read()

        pdf_p = os.path.join(tmp_dir, "report.pdf")
        pdf_res = export_pdf_report(assets, metrics, validation, pdf_p)
        pdf_bytes = b""
        if pdf_res and os.path.exists(pdf_res):
            with open(pdf_res, "rb") as f:
                pdf_bytes = f.read()

    d1, d2, d3 = st.columns(3)
    with d1:
        st.download_button(
            "⬇️ CycloneDX 1.6 CBOM (JSON)",
            data=json.dumps(cbom, indent=2),
            file_name="cbom.json",
            mime="application/json",
            use_container_width=True
        )
    with d2:
        df = _as_df()
        csv_data = df.to_csv(index=False)
        st.download_button(
            "⬇️ Inventory Spreadsheet (CSV)",
            data=csv_data,
            file_name="inventory.csv",
            mime="text/csv",
            use_container_width=True
        )
    with d3:
        st.download_button(
            "⬇️ SARIF 2.1.0 Output (JSON)",
            data=sarif_bytes,
            file_name="findings.sarif",
            mime="application/json",
            use_container_width=True
        )

    r1, r2, r3 = st.columns(3)
    with r1:
        st.download_button(
            "⬇️ Executive Security Report (HTML)",
            data=html_bytes,
            file_name="report.html",
            mime="text/html",
            use_container_width=True
        )
    with r2:
        if pdf_bytes:
            st.download_button(
                "⬇️ Executive Security Report (PDF)",
                data=pdf_bytes,
                file_name="report.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        else:
            st.button("PDF Generation Unavailable", disabled=True, use_container_width=True)
    with r3:
        st.download_button(
            "⬇️ Summary (Markdown)",
            data=md_bytes,
            file_name="summary.md",
            mime="text/markdown",
            use_container_width=True
        )

    st.markdown("---")
    st.subheader("CycloneDX 1.6 CBOM Document Preview")
    st.json(cbom)
    st.caption(f"Validated against official schema: `{validation['schema']}`")


# ===================================================================
# Router
# ===================================================================
PAGES = {
    "Dashboard": page_dashboard,
    "New Scan": page_new_scan,
    "Inventory": page_inventory,
    "Asset Detail": page_asset_detail,
    "Mosca Simulator": page_mosca,
    "Reports": page_reports,
}
PAGES[page]()
