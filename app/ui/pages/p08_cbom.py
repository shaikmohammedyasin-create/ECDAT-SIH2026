"""
Screen 8: ECDAT - CycloneDX 1.6 Cryptographic Bill of Materials (CBOM).
Stitch Screen ID: fc8ab91b7d604b59961d8c2c1327c785
"""
import json
import streamlit as st
import pandas as pd
from app.cbom.cyclonedx import generate_cyclonedx_cbom, validate_cbom
from app.ui.components import render_cbom_status_banner, render_metric_box


def render(assets, navigate_fn):
    st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 16px; border-bottom: 1px solid #30353d; padding-bottom: 10px;">
        <div>
            <div style="display: flex; align-items: center; gap: 8px;">
                <h1 style="font-size: 20px; font-weight: 700; margin: 0; color: #dee2ec;">Cryptographic Bill of Materials (CBOM)</h1>
                <span class="stitch-badge" style="background-color: rgba(109, 229, 117, 0.15); color: #6de575; border: 1px solid rgba(109, 229, 117, 0.4);">
                    CYCLONEDX 1.6 DRAFT-FINAL
                </span>
            </div>
            <div style="font-size: 12px; color: #94a3b8; margin-top: 4px;">
                Official CycloneDX v1.6 Cryptographic Extension specification compliance and formal schema verification
            </div>
        </div>
        <div style="font-family: 'JetBrains Mono', monospace; font-size: 11px; color: #ffc174;">
            Spec: <span style="font-weight: 700;">CycloneDX 1.6</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if not assets:
        st.info("ℹ️ No cryptographic assets loaded yet. Run a scan from the **New Scan** page first.")
        if st.button("Start New Scan →"):
            navigate_fn("New Scan")
        return

    # Real CBOM generation & Schema validation
    cbom = generate_cyclonedx_cbom(assets)
    validation = validate_cbom(cbom)

    is_valid = validation.get("valid", False)
    errors = validation.get("errors", [])
    total_components = len(cbom.get("components", []))

    # 1. Official Schema Status Banner matching Stitch Screen 8
    render_cbom_status_banner(valid=is_valid, errors=len(errors), total_components=total_components)

    # 2. Metric Boxes
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_metric_box("SPECIFICATION FORMAT", "CycloneDX 1.6", "Cryptographic Extension", "#6de575")
    with c2:
        render_metric_box("TOTAL CBOM COMPONENTS", str(total_components), "Normalized Assets", "#dee2ec")
    with c3:
        schema_status = "PASS (0 Errors)" if is_valid else f"FAIL ({len(errors)} Errors)"
        schema_color = "#6de575" if is_valid else "#ef4444"
        render_metric_box("FORMAL JSON VALIDATION", schema_status, "jsonschema Verified", schema_color)
    with c4:
        serial_trunc = cbom.get("serialNumber", "urn:uuid:ecdat")[-12:]
        render_metric_box("SERIAL NUMBER", f"...{serial_trunc}", "Deterministic UUID", "#ffc174")

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # 3. Actions Row
    col_d1, col_d2, col_d3 = st.columns(3)
    with col_d1:
        cbom_json_str = json.dumps(cbom, indent=2)
        st.download_button(
            "⬇️ Export CycloneDX 1.6 (JSON)",
            data=cbom_json_str,
            file_name="cbom.json",
            mime="application/json",
            use_container_width=True
        )
    with col_d2:
        # Convert components to CSV summary
        comp_rows = []
        for c in cbom.get("components", []):
            crypto_data = c.get("cryptoProperties", {})
            comp_rows.append({
                "Name": c.get("name"),
                "Type": c.get("type"),
                "Algorithm": crypto_data.get("algorithmProperties", {}).get("name", "N/A"),
                "PQC Target": crypto_data.get("pqcTarget", "N/A"),
                "Shor Vulnerable": crypto_data.get("shorVulnerable", False),
            })
        csv_data = pd.DataFrame(comp_rows).to_csv(index=False)
        st.download_button(
            "⬇️ Export Component List (CSV)",
            data=csv_data,
            file_name="cbom_components.csv",
            mime="text/csv",
            use_container_width=True
        )
    with col_d3:
        if st.button("Go to Reports & Evidence →", use_container_width=True):
            navigate_fn("Reports & Evidence")

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # 4. Interactive JSON Inspector matching Stitch Screen 8
    st.markdown("""
    <div class="stitch-card-header">
        <div class="stitch-card-title">
            <span class="material-symbols-outlined" style="color: #38bdf8; font-size: 16px;">data_object</span>
            <span>CycloneDX 1.6 Document Tree & Raw Schema Inspector</span>
        </div>
        <div class="stitch-card-sub">cyclonedx.org/schema/bom-1.6.schema.json</div>
    </div>
    """, unsafe_allow_html=True)

    t_tree, t_raw = st.tabs(["Formatted Tree View", "Raw JSON Inspector"])
    with t_tree:
        st.json(cbom)
    with t_raw:
        st.text_area("CycloneDX 1.6 JSON Payload", value=cbom_json_str, height=350, key="txt_cbom_raw", label_visibility="collapsed")
