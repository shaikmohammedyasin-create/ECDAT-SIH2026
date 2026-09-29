"""
Screen 3: ECDAT - Crypto Inventory.
Stitch Screen ID: e2332df3f2d64a2d8661064f212df615
"""
import os
import streamlit as st
import pandas as pd


def render(assets, navigate_fn):
    st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 16px; border-bottom: 1px solid #30353d; padding-bottom: 10px;">
        <div>
            <div style="display: flex; align-items: center; gap: 8px;">
                <h1 style="font-size: 20px; font-weight: 700; margin: 0; color: #dee2ec;">Cryptographic Asset Inventory</h1>
                <span class="stitch-badge" style="background-color: rgba(245, 158, 11, 0.15); color: #ffc174; border: 1px solid rgba(245, 158, 11, 0.4);">
                    NORMALIZED CBOM VIEW
                </span>
            </div>
            <div style="font-size: 12px; color: #94a3b8; margin-top: 4px;">
                Normalized Bill of Cryptographic Materials (CBOM) with Quantum Risk Classification and Evidence Provenance
            </div>
        </div>
        <div style="font-family: 'JetBrains Mono', monospace; font-size: 11px; color: #94a3b8;">
            Total Count: <span style="color: #6de575; font-weight: 700;">""" + str(len(assets) if assets else 0) + """</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if not assets:
        st.info("ℹ️ No cryptographic assets loaded yet. Navigate to **New Scan** to run discovery on a target project.")
        if st.button("Start New Scan →"):
            navigate_fn("New Scan")
        return

    # Build dataframe with original index tracking
    data = []
    for i, a in enumerate(assets):
        data.append({
            "_orig_idx": i,
            "rule_id": a.rule_id or "N/A",
            "algorithm": a.algorithm,
            "key_size": str(a.key_size) if a.key_size else "N/A",
            "mode": a.mode or "N/A",
            "type": a.asset_type.value,
            "usage": a.usage.value,
            "quantum": a.quantum_status.value,
            "threat": "HNDL" if a.hndl_risk else ("TNFL" if a.tnfl_risk else "None"),
            "risk_score": a.risk_score,
            "risk_band": a.risk_band,
            "mosca_margin": round(a.mosca_margin, 1) if a.mosca_margin is not None else "N/A",
            "confidence": a.confidence,
            "file": os.path.basename(a.file_path),
            "line": a.line_number,
        })
    df = pd.DataFrame(data)

    # 1. Filter Toolbar matching Stitch Screen 3
    st.markdown("""
    <div class="stitch-card-lowest" style="margin-bottom: 12px;">
    """, unsafe_allow_html=True)

    f1, f2, f3, f4, f5 = st.columns([2, 1.5, 1.5, 1.5, 1.5])
    with f1:
        search_query = st.text_input("🔍 Search keyword (algo, file, rule ID)", value="", placeholder="e.g. RSA, SHA, certs, ECDAT-SRC")
    with f2:
        algo_filter = st.selectbox("Algorithm", ["All"] + sorted(list(set(df["algorithm"]))))
    with f3:
        quantum_filter = st.selectbox("Quantum Status", ["All"] + sorted(list(set(df["quantum"]))))
    with f4:
        threat_filter = st.selectbox("Threat Flag", ["All", "HNDL", "TNFL", "None"])
    with f5:
        band_filter = st.selectbox("Risk Band", ["All", "Critical", "High", "Medium", "Low", "Info"])

    st.markdown("</div>", unsafe_allow_html=True)

    # Apply filters
    filtered_df = df.copy()
    if search_query:
        q = search_query.lower()
        filtered_df = filtered_df[
            filtered_df["algorithm"].str.lower().str.contains(q) |
            filtered_df["file"].str.lower().str.contains(q) |
            filtered_df["rule_id"].str.lower().str.contains(q) |
            filtered_df["type"].str.lower().str.contains(q)
        ]
    if algo_filter != "All":
        filtered_df = filtered_df[filtered_df["algorithm"] == algo_filter]
    if quantum_filter != "All":
        filtered_df = filtered_df[filtered_df["quantum"] == quantum_filter]
    if threat_filter != "All":
        filtered_df = filtered_df[filtered_df["threat"] == threat_filter]
    if band_filter != "All":
        filtered_df = filtered_df[filtered_df["risk_band"] == band_filter]

    st.markdown(f"""
    <div style="font-family: 'JetBrains Mono'; font-size: 11px; color: #94a3b8; margin-bottom: 8px;">
        Displaying <span style="color: #ffc174; font-weight: 700;">{len(filtered_df)}</span> of {len(df)} discovered cryptographic assets
    </div>
    """, unsafe_allow_html=True)

    # 2. Main Data Table
    display_cols = [
        "rule_id", "algorithm", "key_size", "mode", "type", "usage",
        "quantum", "threat", "risk_score", "risk_band", "confidence", "file", "line"
    ]

    def _color_band(val):
        colors = {
            "Critical": "background-color: #991b1b; color: white; font-weight: bold;",
            "High": "background-color: #9a3412; color: white; font-weight: bold;",
            "Medium": "background-color: #78350f; color: white; font-weight: bold;",
            "Low": "background-color: #064e3b; color: white; font-weight: bold;",
            "Info": "background-color: #1e293b; color: #94a3b8;"
        }
        return colors.get(val, "")

    styled_df = filtered_df[display_cols].style.map(_color_band, subset=["risk_band"])
    st.dataframe(styled_df, use_container_width=True, hide_index=True)

    # 3. Row Inspection Action
    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div class="stitch-card-header">
        <div class="stitch-card-title">
            <span class="material-symbols-outlined" style="color: #ffc174; font-size: 16px;">troubleshoot</span>
            <span>Select Finding for Forensic Inspection</span>
        </div>
        <div class="stitch-card-sub">Jump to Screen 4</div>
    </div>
    """, unsafe_allow_html=True)

    if not filtered_df.empty:
        inspect_options = {
            int(row["_orig_idx"]): f"[{row['risk_band'].upper()} {row['risk_score']:.1f}] {row['rule_id']} · {row['algorithm']} ({row['usage']}) — {row['file']}:{row['line']}"
            for _, row in filtered_df.iterrows()
        }
        c_sel, c_btn = st.columns([4, 1])
        with c_sel:
            selected_orig_idx = st.selectbox(
                "Select Asset to Inspect",
                options=list(inspect_options.keys()),
                format_func=lambda idx: inspect_options[idx],
                label_visibility="collapsed"
            )
        with c_btn:
            if st.button("Inspect Finding →", type="primary", use_container_width=True):
                st.session_state["selected_asset_idx"] = selected_orig_idx
                navigate_fn("Finding Inspector")
