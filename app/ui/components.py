"""
Reusable Stitch UI Components for ECDAT Workstation.
"""
import os
import streamlit as st


def render_topbar(target_path: str = "test_corpus", scan_status: str = "Idle", cbom_valid: bool = True):
    """
    Renders the Stitch top navigation bar with NTRO PS-ID, branch, CycloneDX validation badge,
    scan status, and SecOps token.
    """
    folder_name = os.path.basename(target_path) if target_path else "src/crypto-core"
    valid_color = "#6de575" if cbom_valid else "#ffb4ab"
    valid_text = "CycloneDX v1.6 [VALID]" if cbom_valid else "CycloneDX v1.6 [INVALID]"
    status_dot = "#6de575" if scan_status in ("Idle", "Ready", "Complete") else "#f59e0b"

    html = f"""
    <div class="stitch-topbar">
        <div class="stitch-topbar-left">
            <div class="stitch-brand">
                <span class="material-symbols-outlined" style="color: #f59e0b; font-size: 16px;">shield</span>
                <span>ECDAT // PS-ID: 26164 (NTRO)</span>
            </div>
            <div style="height: 14px; width: 1px; background-color: #30353d;"></div>
            <div style="color: #94a3b8; font-size: 11px; display: flex; align-items: center; gap: 4px;">
                <span class="material-symbols-outlined" style="font-size: 13px;">terminal</span>
                <span>target:{folder_name}</span>
            </div>
            <div style="height: 14px; width: 1px; background-color: #30353d;"></div>
            <div style="color: {valid_color}; font-size: 11px; display: flex; align-items: center; gap: 4px;">
                <span style="display: inline-block; width: 6px; height: 6px; border-radius: 50%; background-color: {valid_color};"></span>
                <span>{valid_text}</span>
            </div>
        </div>
        <div class="stitch-topbar-right">
            <div style="display: flex; align-items: center; gap: 6px; font-size: 11px; color: #94a3b8; background-color: #171c23; padding: 2px 8px; border-radius: 2px; border: 1px solid #30353d;">
                <span style="display: inline-block; width: 6px; height: 6px; border-radius: 50%; background-color: {status_dot};"></span>
                <span>Status: {scan_status}</span>
            </div>
            <div style="height: 14px; width: 1px; background-color: #30353d;"></div>
            <div style="display: flex; align-items: center; gap: 6px;" title="Lead Cryptographer SecOps Token">
                <div style="width: 20px; height: 20px; background-color: #252a32; border: 1px solid #30353d; border-radius: 2px; display: flex; align-items: center; justify-content: center; color: #ffc174; font-weight: bold; font-size: 10px;">
                    NT
                </div>
                <span style="font-size: 11px; color: #94a3b8;">secops-analyst-01</span>
            </div>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_metric_box(title: str, value, subtext: str = None, color: str = None):
    """Renders a single Stitch metric card."""
    val_color = color if color else "var(--stitch-primary)"
    sub_html = f'<div class="stitch-metric-desc">{subtext}</div>' if subtext else ""
    html = f"""
    <div class="stitch-metric-box">
        <div class="stitch-metric-title">{title}</div>
        <div class="stitch-metric-val" style="color: {val_color};">{value}</div>
        {sub_html}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_cbom_status_banner(valid: bool = True, errors: int = 0, total_components: int = 0):
    """Renders the CycloneDX 1.6 formal compliance banner."""
    status_color = "#6de575" if valid else "#ffb4ab"
    status_bg = "rgba(109, 229, 117, 0.08)" if valid else "rgba(255, 180, 171, 0.08)"
    border_color = "rgba(109, 229, 117, 0.35)" if valid else "rgba(255, 180, 171, 0.35)"
    status_text = "PASS ✓ (0 Formal Schema Errors)" if valid else f"FAIL ({errors} Validation Errors)"

    html = f"""
    <div style="background-color: {status_bg}; border: 1px solid {border_color}; border-radius: 4px; padding: 12px 16px; margin-bottom: 16px; display: flex; align-items: center; justify-content: space-between;">
        <div style="display: flex; align-items: center; gap: 12px;">
            <div style="width: 32px; height: 32px; background-color: rgba(109, 229, 117, 0.15); border: 1px solid {status_color}; display: flex; align-items: center; justify-content: center; border-radius: 2px;">
                <span class="material-symbols-outlined" style="color: {status_color}; font-size: 20px;">verified_user</span>
            </div>
            <div>
                <div style="font-family: 'Inter', sans-serif; font-weight: 600; font-size: 13px; color: #dee2ec;">
                    CycloneDX v1.6 Official JSON Schema Validation
                </div>
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 11px; color: #94a3b8; margin-top: 2px;">
                    Specification: CycloneDX 1.6 Cryptographic BOM · Schema: cyclonedx.org/schema/bom-1.6.schema.json
                </div>
            </div>
        </div>
        <div style="text-align: right;">
            <div style="font-family: 'JetBrains Mono', monospace; font-weight: 700; font-size: 12px; color: {status_color};">
                {status_text}
            </div>
            <div style="font-family: 'JetBrains Mono', monospace; font-size: 10px; color: #94a3b8; margin-top: 2px;">
                {total_components} Components Registered
            </div>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)
