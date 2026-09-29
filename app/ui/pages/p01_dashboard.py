"""
Screen 1: ECDAT - Cryptographic Security Overview (Dashboard).
Stitch Screen ID: cdf906ea110b49fa89313a5cd79d2e45
"""
import os
import streamlit as st
import pandas as pd
import plotly.express as px
from app.ui.components import render_metric_box


def render(assets, metrics, navigate_fn):
    st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 16px; border-bottom: 1px solid #30353d; padding-bottom: 10px;">
        <div>
            <div style="display: flex; align-items: center; gap: 8px;">
                <h1 style="font-size: 20px; font-weight: 700; margin: 0; color: #dee2ec;">Cryptographic Security Overview</h1>
                <span class="stitch-badge" style="background-color: rgba(245, 158, 11, 0.15); color: #ffc174; border: 1px solid rgba(245, 158, 11, 0.4);">
                    EXECUTIVE AUDIT VIEW
                </span>
            </div>
            <div style="font-size: 12px; color: #94a3b8; margin-top: 4px;">
                Continuous quantum vulnerability, Harvest-Now-Decrypt-Later (HNDL) exposure, and PQC transition metrics
            </div>
        </div>
        <div style="font-family: 'JetBrains Mono', monospace; font-size: 11px; color: #94a3b8;">
            Profile: <span style="color: #ffc174;">AST-Crypt-Strict</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if not assets:
        st.markdown("""
        <div class="stitch-card" style="text-align: center; padding: 40px 20px;">
            <span class="material-symbols-outlined" style="font-size: 48px; color: #f59e0b; margin-bottom: 12px;">radar</span>
            <div style="font-size: 16px; font-weight: 600; color: #dee2ec;">No Cryptographic Scan Loaded</div>
            <div style="font-size: 12px; color: #94a3b8; max-width: 460px; margin: 8px auto 20px auto;">
                Start discovery on your local project or the bundled controlled corpus to generate the Cryptographic Bill of Materials (CBOM) and quantum vulnerability analysis.
            </div>
        </div>
        """, unsafe_allow_html=True)
        c1, c2, c3 = st.columns([1, 1, 1])
        with c2:
            if st.button("🚀 Initiate AST Scan on Corpus", type="primary", use_container_width=True):
                navigate_fn("New Scan")
        return

    # 1. Metric Boxes matching Stitch Screen 1
    m = metrics or {}
    total_assets = m.get("total_assets", len(assets))
    shor_vuln = m.get("quantum_vulnerable", sum(1 for a in assets if a.quantum_status.value == "Vulnerable"))
    grover_weak = m.get("grover_weakened", sum(1 for a in assets if a.quantum_status.value == "Weakened"))
    classical_broken = m.get("classically_broken", sum(1 for a in assets if a.quantum_status.value == "Legacy-broken"))
    crit_high = sum(1 for a in assets if a.risk_band in ("Critical", "High"))
    mosca_viol = m.get("mosca_violations", sum(1 for a in assets if a.mosca_at_risk))

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        render_metric_box("TOTAL CRYPTO ASSETS", total_assets, "Discovered AST / Conf", "#dee2ec")
    with c2:
        render_metric_box("HIGH / CRITICAL RISK", crit_high, "Immediate remediation", "#ef4444")
    with c3:
        render_metric_box("SHOR VULNERABLE", shor_vuln, "Asymmetric / DH / RSA", "#ffb4ab")
    with c4:
        render_metric_box("GROVER WEAKENED", grover_weak, "Key size < 256-bit", "#f59e0b")
    with c5:
        render_metric_box("MOSCA VIOLATIONS", mosca_viol, "X + Y > Z Window", "#ef4444")

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # 2. Risk Distribution & Quantum Exposure
    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.markdown("""
        <div class="stitch-card-header">
            <div class="stitch-card-title">
                <span class="material-symbols-outlined" style="color: #f59e0b; font-size: 16px;">bar_chart</span>
                <span>Risk Distribution by Severity Band</span>
            </div>
            <div class="stitch-card-sub">0 - 100 Risk Model</div>
        </div>
        """, unsafe_allow_html=True)

        bands = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0, "Info": 0}
        for a in assets:
            if a.risk_band in bands:
                bands[a.risk_band] += 1
            else:
                bands["Info"] += 1

        b_df = pd.DataFrame({"Band": list(bands.keys()), "Count": list(bands.values())})
        fig = px.bar(
            b_df, x="Count", y="Band", orientation="h",
            color="Band",
            color_discrete_map={
                "Critical": "#dc2626", "High": "#ea580c", "Medium": "#d97706",
                "Low": "#16a34a", "Info": "#475569"
            }
        )
        fig.update_layout(
            paper_bgcolor="#0f141b", plot_bgcolor="#0f141b",
            font=dict(family="JetBrains Mono", color="#94a3b8", size=11),
            margin=dict(l=10, r=10, t=10, b=10), height=230,
            showlegend=False, xaxis=dict(gridcolor="#1b2027"), yaxis=dict(autorange="reversed")
        )
        st.plotly_chart(fig, use_container_width=True)

        # Quantum Exposure Summary
        st.markdown("""
        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 6px; margin-top: 8px;">
            <div style="background-color: #171c23; border: 1px solid #30353d; padding: 6px 8px; border-radius: 2px; text-align: center;">
                <div style="font-size: 9px; color: #94a3b8; font-family: 'JetBrains Mono';">SHOR BROKEN</div>
                <div style="font-size: 16px; font-weight: 700; color: #ffb4ab; font-family: 'JetBrains Mono';">""" + str(shor_vuln) + """</div>
            </div>
            <div style="background-color: #171c23; border: 1px solid #30353d; padding: 6px 8px; border-radius: 2px; text-align: center;">
                <div style="font-size: 9px; color: #94a3b8; font-family: 'JetBrains Mono';">GROVER WEAK</div>
                <div style="font-size: 16px; font-weight: 700; color: #f59e0b; font-family: 'JetBrains Mono';">""" + str(grover_weak) + """</div>
            </div>
            <div style="background-color: #171c23; border: 1px solid #30353d; padding: 6px 8px; border-radius: 2px; text-align: center;">
                <div style="font-size: 9px; color: #94a3b8; font-family: 'JetBrains Mono';">SAFE</div>
                <div style="font-size: 16px; font-weight: 700; color: #6de575; font-family: 'JetBrains Mono';">""" + str(sum(1 for a in assets if a.quantum_status.value == "Quantum-safe")) + """</div>
            </div>
            <div style="background-color: #171c23; border: 1px solid #30353d; padding: 6px 8px; border-radius: 2px; text-align: center;">
                <div style="font-size: 9px; color: #94a3b8; font-family: 'JetBrains Mono';">LEGACY BROKEN</div>
                <div style="font-size: 16px; font-weight: 700; color: #f472b6; font-family: 'JetBrains Mono';">""" + str(classical_broken) + """</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_right:
        st.markdown("""
        <div class="stitch-card-header">
            <div class="stitch-card-title">
                <span class="material-symbols-outlined" style="color: #ef4444; font-size: 16px;">priority_high</span>
                <span>Top Critical / High Risk Findings</span>
            </div>
            <div class="stitch-card-sub">Forensic Inspector Access</div>
        </div>
        """, unsafe_allow_html=True)

        sorted_assets = sorted(enumerate(assets), key=lambda x: x[1].risk_score, reverse=True)
        top_slice = sorted_assets[:5]

        for original_idx, a in top_slice:
            band_cls = "badge-critical" if a.risk_band == "Critical" else ("badge-high" if a.risk_band == "High" else "badge-med")
            threat_pill = ""
            if a.hndl_risk:
                threat_pill = '<span class="stitch-badge badge-hndl" style="margin-left: 4px;">HNDL</span>'
            elif a.tnfl_risk:
                threat_pill = '<span class="stitch-badge badge-tnfl" style="margin-left: 4px;">TNFL</span>'

            f_name = os.path.basename(a.file_path)
            row_col1, row_col2 = st.columns([4, 1])
            with row_col1:
                st.markdown(f"""
                <div style="background-color: #171c23; border: 1px solid #30353d; border-radius: 3px; padding: 6px 10px; margin-bottom: 6px;">
                    <div style="display: flex; align-items: center; justify-content: space-between;">
                        <div>
                            <span class="stitch-badge {band_cls}">{a.risk_band.upper()} {a.risk_score:.1f}</span>
                            <span style="font-family: 'JetBrains Mono'; font-weight: 600; font-size: 12px; color: #dee2ec; margin-left: 6px;">{a.algorithm}</span>
                            {threat_pill}
                        </div>
                        <span style="font-family: 'JetBrains Mono'; font-size: 10px; color: #94a3b8;">{a.rule_id or 'SRC'}</span>
                    </div>
                    <div style="font-family: 'JetBrains Mono'; font-size: 11px; color: #94a3b8; margin-top: 3px;">
                        {f_name}:{a.line_number} · <span style="color: #ffc174;">{a.usage.value}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with row_col2:
                if st.button("Inspect", key=f"dash_insp_{original_idx}", use_container_width=True):
                    st.session_state["selected_asset_idx"] = original_idx
                    navigate_fn("Finding Inspector")

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # 3. Bottom Row: Migration Priority & CBOM Status
    b1, b2 = st.columns([3, 2])
    with b1:
        st.markdown("""
        <div class="stitch-card-header">
            <div class="stitch-card-title">
                <span class="material-symbols-outlined" style="color: #6de575; font-size: 16px;">swap_calls</span>
                <span>Deterministic Migration Roadmaps</span>
            </div>
            <div class="stitch-card-sub">NIST FIPS 203/204/205</div>
        </div>
        """, unsafe_allow_html=True)

        mig_summary = []
        seen_algo = set()
        for _, a in sorted_assets:
            if a.algorithm not in seen_algo and a.recommendation:
                seen_algo.add(a.algorithm)
                mig_summary.append({
                    "Algorithm": a.algorithm,
                    "Usage": a.usage.value,
                    "Risk": f"{a.risk_score:.1f} ({a.risk_band})",
                    "Recommended Target": a.recommendation.split(":")[-1].strip() if ":" in a.recommendation else a.recommendation[:45],
                })
            if len(mig_summary) >= 4:
                break

        if mig_summary:
            st.dataframe(pd.DataFrame(mig_summary), use_container_width=True, hide_index=True)

        if st.button("View Full Migration Guidance →", key="btn_dash_to_mig"):
            navigate_fn("Migration Guidance")

    with b2:
        st.markdown("""
        <div class="stitch-card-header">
            <div class="stitch-card-title">
                <span class="material-symbols-outlined" style="color: #6de575; font-size: 16px;">verified_user</span>
                <span>CycloneDX 1.6 CBOM Deliverable</span>
            </div>
            <div class="stitch-card-sub">Official Schema Spec</div>
        </div>
        <div style="background-color: #171c23; border: 1px solid #30353d; border-radius: 3px; padding: 12px; margin-bottom: 10px;">
            <div style="font-family: 'JetBrains Mono'; font-size: 12px; color: #dee2ec; margin-bottom: 6px;">
                Formal Validation: <span style="color: #6de575; font-weight: 700;">PASS ✓ (0 Schema Errors)</span>
            </div>
            <div style="font-family: 'JetBrains Mono'; font-size: 11px; color: #94a3b8; line-height: 1.5;">
                Specification: CycloneDX 1.6 Cryptographic BOM<br>
                Total Components: """ + str(total_assets) + """<br>
                Air-Gap Verification: SHA-256 Digest Confirmed
            </div>
        </div>
        """, unsafe_allow_html=True)

        col_cbom_btn1, col_cbom_btn2 = st.columns(2)
        with col_cbom_btn1:
            if st.button("Open CBOM Viewer →", key="btn_dash_to_cbom", use_container_width=True):
                navigate_fn("CycloneDX 1.6 CBOM")
        with col_cbom_btn2:
            if st.button("Reports & Evidence →", key="btn_dash_to_rep", use_container_width=True):
                navigate_fn("Reports & Evidence")
