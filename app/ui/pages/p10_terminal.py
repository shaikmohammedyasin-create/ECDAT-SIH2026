"""
Screen 9 / 10: ECDAT - Terminal & Scan Execution Log.
Stitch Screen ID: 6d09dab7933747e587da348a113551ac
"""
import time
import streamlit as st
from app.ui.components import render_metric_box


def render(scan_logs, metrics, navigate_fn):
    st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 16px; border-bottom: 1px solid #30353d; padding-bottom: 10px;">
        <div>
            <div style="display: flex; align-items: center; gap: 8px;">
                <h1 style="font-size: 20px; font-weight: 700; margin: 0; color: #dee2ec;">Terminal / Scan Log</h1>
                <span class="stitch-badge" style="background-color: rgba(56, 189, 248, 0.15); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.4);">
                    REAL-TIME TELEMETRY
                </span>
            </div>
            <div style="font-size: 12px; color: #94a3b8; margin-top: 4px;">
                Deterministic engine event stream, AST discovery stages, and cryptographic normalization audit trail
            </div>
        </div>
        <div style="font-family: 'JetBrains Mono', monospace; font-size: 11px; color: #6de575; display: flex; align-items: center; gap: 6px;">
            <span style="display: inline-block; width: 6px; height: 6px; border-radius: 50%; background-color: #6de575;"></span>
            Session: airgap-node-01 [LIVE]
        </div>
    </div>
    """, unsafe_allow_html=True)

    m = metrics or {}

    # 1. Telemetry Strip matching Stitch Screen 9
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_metric_box("ACTIVE PROCESS", "ECDAT AST Engine", "PID: local_airgap", "#6de575")
    with c2:
        scan_t = f"{m.get('scan_time_s', 0.0):.3f}s"
        render_metric_box("LAST EXECUTION TIME", scan_t, "Pipeline Execution", "#38bdf8")
    with c3:
        tot = m.get("total_assets", 0)
        render_metric_box("TOTAL IDENTIFIED ASSETS", str(tot), "Normalized Entities", "#ffc174")
    with c4:
        render_metric_box("LOG EVENTS RECORDED", str(len(scan_logs) if scan_logs else 0), "Stream Buffer", "#dee2ec")

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # 2. Terminal Controls Toolbar
    col_f1, col_f2, col_f3 = st.columns([2, 1, 1])
    with col_f1:
        level_filter = st.selectbox("Filter Log Level", ["ALL", "INFO", "SUCCESS", "WARN", "ERROR"], key="term_filter")
    with col_f2:
        if st.button("🗑️ Clear Terminal Buffer"):
            st.session_state["scan_logs"] = []
            st.rerun()
    with col_f3:
        log_text = "\n".join([f"[{t}] [{lvl}] {msg}" for t, lvl, msg in (scan_logs or [])])
        st.download_button(
            "⬇️ Export Log File",
            data=log_text if log_text else "[No log entries recorded]",
            file_name="ecdat_scan.log",
            mime="text/plain",
            use_container_width=True
        )

    # 3. Interactive Terminal Window
    st.markdown("""
    <div style="background-color: #06090e; border: 1px solid #30353d; border-radius: 4px; padding: 12px 16px; margin-top: 10px;">
        <div style="display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid #1e293b; padding-bottom: 8px; margin-bottom: 10px;">
            <div style="display: flex; align-items: center; gap: 6px;">
                <span style="display: inline-block; width: 10px; height: 10px; border-radius: 50%; background-color: #ef4444;"></span>
                <span style="display: inline-block; width: 10px; height: 10px; border-radius: 50%; background-color: #f59e0b;"></span>
                <span style="display: inline-block; width: 10px; height: 10px; border-radius: 50%; background-color: #10b981;"></span>
                <span style="font-family: 'JetBrains Mono'; font-size: 11px; color: #94a3b8; margin-left: 8px;">bash: ecdat-cli v2.4 (air-gapped session)</span>
            </div>
            <span style="font-family: 'JetBrains Mono'; font-size: 10px; color: #64748b;">UTF-8 · CP1252_SAFE</span>
        </div>
        <div style="font-family: 'JetBrains Mono'; font-size: 11px; line-height: 1.6; max-height: 420px; overflow-y: auto;">
    """, unsafe_allow_html=True)

    if not scan_logs:
        st.markdown("""
            <div style="color: #64748b; font-style: italic;">
                [System Idle] No scan pipeline executed in this session yet. Navigate to <strong>New Scan</strong> to trigger AST discovery.
            </div>
        """, unsafe_allow_html=True)
    else:
        for t_stamp, lvl, msg in scan_logs:
            if level_filter != "ALL" and lvl != level_filter:
                continue

            lvl_color = "#38bdf8"
            if lvl == "SUCCESS":
                lvl_color = "#4ade80"
            elif lvl == "WARN":
                lvl_color = "#f59e0b"
            elif lvl == "ERROR":
                lvl_color = "#ef4444"

            st.markdown(f"""
            <div style="display: flex; gap: 8px; margin-bottom: 2px;">
                <span style="color: #64748b;">[{t_stamp}]</span>
                <span style="color: {lvl_color}; font-weight: 700; width: 68px;">[{lvl}]</span>
                <span style="color: #cbd5e1;">{msg}</span>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("</div></div>", unsafe_allow_html=True)
