"""
ECDAT — Enterprise Cryptographic Discovery & Analysis Tool (SIH 2026 PS ID 26164 NTRO).
Security Workstation Frontend.
Source of Truth: Stitch Project 'ECDAT Security Workstation' (ID: 15951502437945520827).

Complete 11-Screen Workstation Architecture:
1. Dashboard (Cryptographic Security Overview)
2. New Scan (New Scan Configuration & Multi-Collector Execution)
3. Crypto Inventory (Searchable Normalized CBOM View)
4. Finding Inspector (Deep AST Forensic Evidence & Asset Detail)
5. Mosca Simulator (Interactive Planning Horizons X + Y > Z)
6. Risk Analysis (5-Factor Deterministic Quantitative Risk Engine)
7. Migration Guidance (NIST FIPS 203/204/205 Transition Guidance)
8. CycloneDX 1.6 CBOM (Specification Compliance & JSON Schema Validation)
9. Reports & Evidence (6 Deliverable Formats: HTML, PDF, SARIF, CSV, JSON, MD)
10. Terminal / Log (Real-Time Engine Execution Telemetry Stream)
11. Settings (Workstation Parameters & Air-Gap Security Policies)
"""
import os
import sys
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import streamlit as st
from app.pipeline import run_full_scan
from app.cbom.cyclonedx import generate_cyclonedx_cbom, validate_cbom

from app.ui.styles import STITCH_CSS
from app.ui.components import render_topbar

# Screen modules
from app.ui.pages import p01_dashboard
from app.ui.pages import p02_new_scan
from app.ui.pages import p03_inventory
from app.ui.pages import p04_inspector
from app.ui.pages import p05_mosca
from app.ui.pages import p06_risk
from app.ui.pages import p07_migration
from app.ui.pages import p08_cbom
from app.ui.pages import p09_reports
from app.ui.pages import p10_terminal
from app.ui.pages import p11_settings

st.set_page_config(
    page_title="ECDAT // Security Workstation",
    layout="wide",
    page_icon="🛡️",
    initial_sidebar_state="expanded"
)

# Inject Stitch Design System CSS
st.markdown(STITCH_CSS, unsafe_allow_html=True)

DEFAULT_CORPUS = os.path.abspath("test_corpus")

# -------------------------------------------------------------------------
# State Initialization
# -------------------------------------------------------------------------
if "active_page" not in st.session_state:
    st.session_state["active_page"] = "Dashboard"

if "scan_path" not in st.session_state:
    st.session_state["scan_path"] = DEFAULT_CORPUS

if "scenario_year" not in st.session_state:
    st.session_state["scenario_year"] = 2035

if "x_lifetime" not in st.session_state:
    st.session_state["x_lifetime"] = 10.0

if "y_migration" not in st.session_state:
    st.session_state["y_migration"] = 3.0

if "selected_asset_idx" not in st.session_state:
    st.session_state["selected_asset_idx"] = 0

if "scan_logs" not in st.session_state:
    st.session_state["scan_logs"] = []

if "assets" not in st.session_state or st.session_state["assets"] is None:
    # Auto-initialize with controlled test corpus on first launch
    if os.path.exists(DEFAULT_CORPUS):
        try:
            init_logs = []
            def _init_log(lvl, msg):
                init_logs.append((time.strftime("%H:%M:%S"), lvl, msg))
            assets, metrics = run_full_scan(
                DEFAULT_CORPUS,
                scenario_year=st.session_state["scenario_year"],
                x_lifetime=st.session_state["x_lifetime"],
                y_migration=st.session_state["y_migration"],
                log_callback=_init_log
            )
            st.session_state["assets"] = assets
            st.session_state["metrics"] = metrics
            st.session_state["scan_logs"] = init_logs
        except Exception as e:
            st.session_state["assets"] = []
            st.session_state["metrics"] = {}
    else:
        st.session_state["assets"] = []
        st.session_state["metrics"] = {}


def execute_scan(path: str, log_callback=None):
    """Executes the complete scan pipeline and updates session state."""
    assets, metrics = run_full_scan(
        path,
        scenario_year=st.session_state["scenario_year"],
        x_lifetime=st.session_state["x_lifetime"],
        y_migration=st.session_state["y_migration"],
        log_callback=log_callback
    )
    st.session_state["assets"] = assets
    st.session_state["metrics"] = metrics
    st.session_state["scan_path"] = path
    return assets, metrics


def navigate_to(page_name: str):
    """Inter-page router transition."""
    st.session_state["active_page"] = page_name
    st.rerun()


# -------------------------------------------------------------------------
# Sidebar Shell matching Stitch SideNavBar
# -------------------------------------------------------------------------
PAGE_LIST = [
    "Dashboard",
    "New Scan",
    "Crypto Inventory",
    "Finding Inspector",
    "Mosca Simulator",
    "Risk Analysis",
    "Migration Guidance",
    "CycloneDX 1.6 CBOM",
    "Reports & Evidence",
    "Terminal / Log",
    "Settings"
]

with st.sidebar:
    # SideNav Header matching Stitch
    st.markdown("""
    <div style="padding: 0 4px 10px 4px; border-bottom: 1px solid #30353d; margin-bottom: 10px;">
        <div style="display: flex; align-items: center; justify-content: space-between;">
            <div style="display: flex; align-items: center; gap: 6px;">
                <span class="material-symbols-outlined" style="color: #ffc174; font-size: 18px;">security</span>
                <span style="font-family: 'JetBrains Mono'; font-weight: 700; font-size: 13px; color: #ffc174; letter-spacing: -0.01em;">
                    ECDAT Engine
                </span>
            </div>
            <span style="background-color: rgba(109, 229, 117, 0.15); border: 1px solid rgba(109, 229, 117, 0.4); color: #6de575; font-family: 'JetBrains Mono'; font-size: 9px; font-weight: 700; padding: 1px 4px; border-radius: 2px;">
                ONLINE
            </span>
        </div>
        <div style="font-family: 'JetBrains Mono'; font-size: 10px; color: #94a3b8; margin-top: 3px;">
            SIH 2026 // NTRO SEC (PS 26164)
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Primary Action CTA Button matching Stitch
    if st.button("🚀 Initiate AST Scan", type="primary", use_container_width=True):
        navigate_to("New Scan")

    st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)

    # Active page index
    active_idx = PAGE_LIST.index(st.session_state["active_page"]) if st.session_state["active_page"] in PAGE_LIST else 0

    selected_page = st.radio(
        "Navigation",
        PAGE_LIST,
        index=active_idx,
        label_visibility="collapsed",
        key="stitch_nav_radio"
    )

    if selected_page != st.session_state["active_page"]:
        st.session_state["active_page"] = selected_page
        st.rerun()

    # SideNav Footer matching Stitch
    total_found = len(st.session_state["assets"]) if st.session_state.get("assets") else 0
    st.markdown(f"""
    <div style="border-top: 1px solid #30353d; padding-top: 12px; margin-top: 20px; font-family: 'JetBrains Mono'; font-size: 10px;">
        <div style="display: flex; align-items: center; justify-content: space-between; color: #6de575; margin-bottom: 6px;">
            <div style="display: flex; align-items: center; gap: 4px;">
                <span class="material-symbols-outlined" style="font-size: 13px;">check_circle</span>
                <span>System Health: Optimal</span>
            </div>
            <span style="color: #94a3b8;">v2.4</span>
        </div>
        <div style="background-color: #171c23; border: 1px solid #252a32; border-radius: 2px; padding: 6px 8px; color: #94a3b8; display: flex; justify-content: space-between;">
            <span>AIR-GAP ID: NTRO-8841</span>
            <span style="color: #ffc174; font-weight: 700;">SEC-3</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


# -------------------------------------------------------------------------
# Top Bar & Main Content Viewport
# -------------------------------------------------------------------------
current_assets = st.session_state.get("assets", [])
current_metrics = st.session_state.get("metrics", {})
current_path = st.session_state.get("scan_path", DEFAULT_CORPUS)
scan_status = "Complete" if current_assets else "Idle"

# Render Top Bar
render_topbar(target_path=current_path, scan_status=scan_status, cbom_valid=True)

# Dispatch to Screen
curr_page = st.session_state["active_page"]

if curr_page == "Dashboard":
    p01_dashboard.render(current_assets, current_metrics, navigate_to)
elif curr_page == "New Scan":
    p02_new_scan.render(execute_scan, navigate_to)
elif curr_page == "Crypto Inventory":
    p03_inventory.render(current_assets, navigate_to)
elif curr_page == "Finding Inspector":
    p04_inspector.render(current_assets, navigate_to)
elif curr_page == "Mosca Simulator":
    p05_mosca.render(current_assets, execute_scan, navigate_to)
elif curr_page == "Risk Analysis":
    p06_risk.render(current_assets, navigate_to)
elif curr_page == "Migration Guidance":
    p07_migration.render(current_assets, navigate_to)
elif curr_page == "CycloneDX 1.6 CBOM":
    p08_cbom.render(current_assets, navigate_to)
elif curr_page == "Reports & Evidence":
    p09_reports.render(current_assets, current_metrics, navigate_to)
elif curr_page == "Terminal / Log":
    p10_terminal.render(st.session_state.get("scan_logs", []), current_metrics, navigate_to)
elif curr_page == "Settings":
    p11_settings.render(navigate_to)
else:
    st.error(f"Unknown page: {curr_page}")
