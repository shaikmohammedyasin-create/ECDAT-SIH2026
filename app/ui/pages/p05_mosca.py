"""
Screen 5: ECDAT - Mosca Risk Simulator.
Stitch Screen ID: 826a2eeceba74e198c93dc8191a5d9a9
"""
import streamlit as st
from app.ui.components import render_metric_box

CURRENT_YEAR = 2026


def render(assets, scan_executor_fn, navigate_fn):
    st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 16px; border-bottom: 1px solid #30353d; padding-bottom: 10px;">
        <div>
            <div style="display: flex; align-items: center; gap: 8px;">
                <h1 style="font-size: 20px; font-weight: 700; margin: 0; color: #dee2ec;">Mosca Risk Simulator</h1>
                <span class="stitch-badge" style="background-color: rgba(245, 158, 11, 0.15); color: #ffc174; border: 1px solid rgba(245, 158, 11, 0.4);">
                    THEOREM: X + Y > Z
                </span>
            </div>
            <div style="font-size: 12px; color: #94a3b8; margin-top: 4px;">
                Evaluate whether migration time overlaps security lifetime against organizational quantum readiness horizons
            </div>
        </div>
        <div style="font-family: 'JetBrains Mono', monospace; font-size: 11px; color: #ffc174;">
            Planning Baseline: <span style="font-weight: 700;">Year 2026</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="background-color: rgba(245, 158, 11, 0.08); border: 1px solid rgba(245, 158, 11, 0.3); border-radius: 4px; padding: 10px 14px; margin-bottom: 16px;">
        <div style="color: #ffc174; font-family: 'JetBrains Mono'; font-weight: 700; font-size: 11px;">
            ⚠️ METHODOLOGICAL DISCLAIMER — PLANNING SCENARIOS
        </div>
        <div style="color: #dee2ec; font-size: 11px; margin-top: 3px; line-height: 1.4;">
            The years 2030, 2035, and 2040 are strategic risk planning scenarios for organizational migration readiness, 
            <strong>NOT physical predictions or forecasts</strong> of when a Cryptographically Relevant Quantum Computer (CRQC) will be realized.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 1. Parameter Inputs
    st.markdown("""
    <div class="stitch-card-header">
        <div class="stitch-card-title">
            <span class="material-symbols-outlined" style="color: #f59e0b; font-size: 16px;">tune</span>
            <span>Simulation Parameters (X, Y, Z)</span>
        </div>
        <div class="stitch-card-sub">Dynamic Model Inputs</div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        default_scenario = st.session_state.get("scenario_year", 2035)
        scenario_year = st.selectbox(
            "CRQC Scenario Year (Z Horizon)",
            [2030, 2035, 2040, 2045, 2050],
            index=[2030, 2035, 2040, 2045, 2050].index(default_scenario) if default_scenario in [2030, 2035, 2040, 2045, 2050] else 1,
            help="Year by which a CRQC capability is assumed in this planning scenario."
        )
    with c2:
        default_x = st.session_state.get("x_lifetime", 10.0)
        x_lifetime = st.slider(
            "X: Data / Trust Lifetime (years)",
            1.0, 30.0, float(default_x), 0.5,
            help="How long the encrypted data or public-key trust must remain secret or unforgeable."
        )
    with c3:
        default_y = st.session_state.get("y_migration", 3.0)
        y_migration = st.slider(
            "Y: Migration & Deployment Time (years)",
            0.5, 15.0, float(default_y), 0.5,
            help="How long it takes to design, test, and deploy post-quantum cryptographic algorithms."
        )

    # Calculate Mosca Theorem
    z_horizon = scenario_year - CURRENT_YEAR
    required_window = x_lifetime + y_migration
    security_margin = z_horizon - required_window
    is_at_risk = security_margin < 0

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # 2. Result Metrics Cards matching Stitch Screen 5
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        render_metric_box("REQUIRED WINDOW (X + Y)", f"{required_window:.1f} yr", f"X={x_lifetime}y + Y={y_migration}y", "#dee2ec")
    with m2:
        render_metric_box("CRQC HORIZON (Z)", f"{z_horizon} yr", f"Scenario Year: {scenario_year}", "#38bdf8")
    with m3:
        margin_color = "#ef4444" if is_at_risk else "#6de575"
        render_metric_box("SECURITY MARGIN [Z - (X+Y)]", f"{security_margin:.1f} yr", "Positive = Secure Window", margin_color)
    with m4:
        status_label = "🚨 AT RISK" if is_at_risk else "✅ WITHIN WINDOW"
        status_color = "#ef4444" if is_at_risk else "#6de575"
        render_metric_box("THEOREM VERDICT", status_label, "X + Y > Z Condition", status_color)

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    # 3. Visual Timeline Explanation
    st.markdown(f"""
    <div style="background-color: #171c23; border: 1px solid #30353d; border-radius: 4px; padding: 14px 16px; margin-bottom: 16px;">
        <div style="font-family: 'JetBrains Mono'; font-weight: 600; font-size: 13px; color: #dee2ec; margin-bottom: 8px;">
            Mathematical Interpretation for Scenario {scenario_year}
        </div>
        <div style="font-family: 'JetBrains Mono'; font-size: 11px; color: #94a3b8; line-height: 1.6;">
            • Current Year: <strong>{CURRENT_YEAR}</strong><br>
            • Time to CRQC (Z): <strong>{z_horizon} years</strong> ({CURRENT_YEAR} → {scenario_year})<br>
            • Protection Duration Required (X + Y): <strong>{required_window:.1f} years</strong> (Migration {y_migration}y + Secrecy {x_lifetime}y)<br>
            • Difference [Z − (X + Y)]: <strong style="color: {'#ef4444' if is_at_risk else '#6de575'};">{security_margin:.1f} years</strong>
        </div>
        <div style="margin-top: 10px; font-size: 12px; color: {'#ffb4ab' if is_at_risk else '#86efac'};">
            {'🚨 <strong>Urgent Remediation Required:</strong> Data intercepted today will still require confidentiality when a quantum computer arrives. PQC transition must begin immediately.' if is_at_risk else '✅ <strong>Positive Transition Buffer:</strong> Migration completed within safe parameters before the planning horizon.'}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 4. Recomputation Action
    st.markdown("""
    <div class="stitch-card-header">
        <div class="stitch-card-title">
            <span class="material-symbols-outlined" style="color: #6de575; font-size: 16px;">sync</span>
            <span>Dynamic Model Re-computation</span>
        </div>
        <div class="stitch-card-sub">Propagate Parameters Across Active Inventory</div>
    </div>
    """, unsafe_allow_html=True)

    c_btn1, c_btn2 = st.columns([2, 1])
    with c_btn1:
        st.markdown("""
        <div style="font-size: 11px; color: #94a3b8;">
            Apply these parameters to recalculate all asset margins and risk scores in the active scan.
        </div>
        """, unsafe_allow_html=True)
    with c_btn2:
        if st.button("Apply Parameters to Active Scan", type="primary", use_container_width=True):
            st.session_state["scenario_year"] = scenario_year
            st.session_state["x_lifetime"] = x_lifetime
            st.session_state["y_migration"] = y_migration
            if st.session_state.get("scan_path"):
                scan_executor_fn(st.session_state["scan_path"])
                st.success("Re-evaluated complete inventory with updated parameters!")
                st.rerun()
