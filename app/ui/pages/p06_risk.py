"""
Screen 6: ECDAT - Cryptographic Risk Analysis.
Stitch Screen ID: 22fc4a9277854090b1288eb1bfb07db1
"""
import os
import streamlit as st
import pandas as pd
import plotly.express as px
from app.ui.components import render_metric_box


def render(assets, navigate_fn):
    st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 16px; border-bottom: 1px solid #30353d; padding-bottom: 10px;">
        <div>
            <div style="display: flex; align-items: center; gap: 8px;">
                <h1 style="font-size: 20px; font-weight: 700; margin: 0; color: #dee2ec;">Cryptographic Risk Analysis</h1>
                <span class="stitch-badge" style="background-color: rgba(245, 158, 11, 0.15); color: #ffc174; border: 1px solid rgba(245, 158, 11, 0.4);">
                    DETERMINISTIC EVALUATION
                </span>
            </div>
            <div style="font-size: 12px; color: #94a3b8; margin-top: 4px;">
                Quantitative 0–100 risk scoring engine factoring quantum vulnerability, business criticality, exposure surface, and crypto agility
            </div>
        </div>
        <div style="font-family: 'JetBrains Mono', monospace; font-size: 11px; color: #94a3b8;">
            Formula Weighting: <span style="color: #6de575;">5-FACTOR COMPOSITE</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if not assets:
        st.info("ℹ️ No assets available. Run a scan from the **New Scan** page first.")
        if st.button("Start New Scan →"):
            navigate_fn("New Scan")
        return

    # 1. Deterministic Formula Banner matching Stitch Screen 6
    st.markdown("""
    <div style="background-color: #171c23; border: 1px solid #30353d; border-radius: 4px; padding: 12px 16px; margin-bottom: 16px;">
        <div style="font-family: 'JetBrains Mono'; font-weight: 600; font-size: 11px; color: #ffc174; text-transform: uppercase;">
            ECDAT Deterministic Risk Formulation (0–100 Score)
        </div>
        <div style="font-family: 'JetBrains Mono'; font-size: 12px; color: #dee2ec; margin-top: 6px; padding: 8px; background-color: #090f15; border: 1px solid #252a32; border-radius: 2px;">
            RiskScore = 100 × [ 0.35·QuantumExposure + 0.25·BusinessCriticality + 0.15·ExposureSurface + 0.15·DataSensitivity + 0.10·(1 − CryptoAgility) ]
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 2. Risk Metrics & Factor Breakdown Cards
    avg_score = sum(a.risk_score for a in assets) / len(assets) if assets else 0
    crit_count = sum(1 for a in assets if a.risk_band == "Critical")
    high_count = sum(1 for a in assets if a.risk_band == "High")
    med_count = sum(1 for a in assets if a.risk_band == "Medium")
    low_count = sum(1 for a in assets if a.risk_band in ("Low", "Info"))

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        render_metric_box("AVERAGE RISK SCORE", f"{avg_score:.1f}", "Overall Portfolio", "#f59e0b")
    with c2:
        render_metric_box("CRITICAL RISK (>=80)", f"{crit_count}", "Immediate Priority", "#ef4444")
    with c3:
        render_metric_box("HIGH RISK (60-79)", f"{high_count}", "Near-term Target", "#f97316")
    with c4:
        render_metric_box("MEDIUM RISK (40-59)", f"{med_count}", "Scheduled Migration", "#f59e0b")
    with c5:
        render_metric_box("LOW RISK (<40)", f"{low_count}", "Monitored / Safe", "#10b981")

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # 3. Factor Analysis Grid
    st.markdown("""
    <div class="stitch-card-header">
        <div class="stitch-card-title">
            <span class="material-symbols-outlined" style="color: #38bdf8; font-size: 16px;">analytics</span>
            <span>Risk Factor Contribution Weights</span>
        </div>
        <div class="stitch-card-sub">Factor Decomposition</div>
    </div>
    """, unsafe_allow_html=True)

    f1, f2, f3, f4, f5 = st.columns(5)
    with f1:
        st.markdown("""
        <div class="stitch-card-lowest" style="text-align: center;">
            <div style="font-size: 10px; color: #94a3b8; font-family: 'JetBrains Mono';">1. QUANTUM EXPOSURE</div>
            <div style="font-size: 18px; font-weight: 700; color: #ffb4ab; font-family: 'JetBrains Mono'; margin: 4px 0;">35%</div>
            <div style="font-size: 10px; color: #94a3b8;">Shor vs Grover impact</div>
        </div>
        """, unsafe_allow_html=True)
    with f2:
        st.markdown("""
        <div class="stitch-card-lowest" style="text-align: center;">
            <div style="font-size: 10px; color: #94a3b8; font-family: 'JetBrains Mono';">2. BUSINESS CRITICALITY</div>
            <div style="font-size: 18px; font-weight: 700; color: #ffc174; font-family: 'JetBrains Mono'; margin: 4px 0;">25%</div>
            <div style="font-size: 10px; color: #94a3b8;">Core trust anchor / auth</div>
        </div>
        """, unsafe_allow_html=True)
    with f3:
        st.markdown("""
        <div class="stitch-card-lowest" style="text-align: center;">
            <div style="font-size: 10px; color: #94a3b8; font-family: 'JetBrains Mono';">3. EXPOSURE SURFACE</div>
            <div style="font-size: 18px; font-weight: 700; color: #38bdf8; font-family: 'JetBrains Mono'; margin: 4px 0;">15%</div>
            <div style="font-size: 10px; color: #94a3b8;">External vs internal call</div>
        </div>
        """, unsafe_allow_html=True)
    with f4:
        st.markdown("""
        <div class="stitch-card-lowest" style="text-align: center;">
            <div style="font-size: 10px; color: #94a3b8; font-family: 'JetBrains Mono';">4. DATA SENSITIVITY</div>
            <div style="font-size: 18px; font-weight: 700; color: #f59e0b; font-family: 'JetBrains Mono'; margin: 4px 0;">15%</div>
            <div style="font-size: 10px; color: #94a3b8;">Long-lived secret / PII</div>
        </div>
        """, unsafe_allow_html=True)
    with f5:
        st.markdown("""
        <div class="stitch-card-lowest" style="text-align: center;">
            <div style="font-size: 10px; color: #94a3b8; font-family: 'JetBrains Mono';">5. (1 - AGILITY)</div>
            <div style="font-size: 18px; font-weight: 700; color: #6de575; font-family: 'JetBrains Mono'; margin: 4px 0;">10%</div>
            <div style="font-size: 10px; color: #94a3b8;">Hardcoded vs pluggable</div>
        </div>
        """, unsafe_allow_html=True)

    # 4. Hygiene-Critical Classical Broken Alert
    hygiene_assets = [a for a in assets if a.hygiene_critical or a.quantum_status.value == "Legacy-broken"]
    if hygiene_assets:
        st.markdown("""
        <div style="background-color: rgba(147, 0, 10, 0.15); border: 1px solid rgba(255, 180, 171, 0.3); border-radius: 4px; padding: 10px 14px; margin-top: 14px; margin-bottom: 14px;">
            <div style="color: #ffb4ab; font-family: 'JetBrains Mono'; font-weight: 700; font-size: 11px;">
                ⚠️ HYGIENE-CRITICAL FINDINGS DETECTED ({len(hygiene_assets)} ASSETS)
            </div>
            <div style="color: #dee2ec; font-size: 11px; margin-top: 3px;">
                Legacy broken primitives (e.g., MD5, SHA-1, DES/3DES) are vulnerable to classical collision and brute-force attacks today. 
                Remediation is required immediately, independent of quantum computing capabilities.
            </div>
        </div>
        """.replace("{len(hygiene_assets)}", str(len(hygiene_assets))), unsafe_allow_html=True)

    # 5. Top Priority Findings Table with Factor Columns
    st.markdown("""
    <div class="stitch-card-header">
        <div class="stitch-card-title">
            <span class="material-symbols-outlined" style="color: #f59e0b; font-size: 16px;">table_chart</span>
            <span>Cryptographic Assets Ranked by Deterministic Risk Score</span>
        </div>
        <div class="stitch-card-sub">Forensic Inspection Available</div>
    </div>
    """, unsafe_allow_html=True)

    sorted_assets = sorted(enumerate(assets), key=lambda x: x[1].risk_score, reverse=True)
    table_data = []
    for orig_idx, a in sorted_assets:
        table_data.append({
            "_orig_idx": orig_idx,
            "Rule ID": a.rule_id or "N/A",
            "Algorithm": a.algorithm,
            "Risk Score": round(a.risk_score, 1),
            "Risk Band": a.risk_band,
            "Quantum Vuln": a.quantum_status.value,
            "Threat Flag": "HNDL" if a.hndl_risk else ("TNFL" if a.tnfl_risk else "None"),
            "Exposure": a.exposure,
            "File": os.path.basename(a.file_path),
            "Line": a.line_number,
        })

    df_risk = pd.DataFrame(table_data)
    st.dataframe(df_risk.drop(columns=["_orig_idx"]), use_container_width=True, hide_index=True)

    if not df_risk.empty:
        c_sel, c_btn = st.columns([4, 1])
        with c_sel:
            chosen = st.selectbox(
                "Select Asset to Inspect from Risk Table",
                options=df_risk["_orig_idx"].tolist(),
                format_func=lambda idx: f"[{assets[idx].risk_band.upper()} {assets[idx].risk_score:.1f}] {assets[idx].rule_id or 'SRC'} · {assets[idx].algorithm} — {os.path.basename(assets[idx].file_path)}:{assets[idx].line_number}",
                label_visibility="collapsed"
            )
        with c_btn:
            if st.button("Inspect Asset →", type="primary", use_container_width=True):
                st.session_state["selected_asset_idx"] = chosen
                navigate_fn("Finding Inspector")
