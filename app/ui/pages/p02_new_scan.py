"""
Screen 2: ECDAT - New Scan Configuration & Execution.
Stitch Screen ID: 8892df4e7ebe45be889b05d60c38f409
"""
import os
import time
import streamlit as st
from app.pipeline import run_full_scan
from app.cbom.cyclonedx import generate_cyclonedx_cbom, validate_cbom


def render(scan_executor_fn, navigate_fn):
    st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 16px; border-bottom: 1px solid #30353d; padding-bottom: 10px;">
        <div>
            <div style="display: flex; align-items: center; gap: 8px;">
                <h1 style="font-size: 20px; font-weight: 700; margin: 0; color: #dee2ec;">New Scan Configuration</h1>
                <span class="stitch-badge" style="background-color: rgba(245, 158, 11, 0.15); color: #ffc174; border: 1px solid rgba(245, 158, 11, 0.4);">
                    PROFILE: AST-CRYPT-STRICT
                </span>
            </div>
            <div style="font-size: 12px; color: #94a3b8; margin-top: 4px;">
                Configure AST discovery collectors, dependency manifests, and cryptographic certificates for air-gapped evaluation
            </div>
        </div>
        <div style="font-family: 'JetBrains Mono', monospace; font-size: 11px; color: #6de575; display: flex; align-items: center; gap: 6px;">
            <span style="display: inline-block; width: 6px; height: 6px; border-radius: 50%; background-color: #6de575;"></span>
            Strict Path Sandbox Activated
        </div>
    </div>
    """, unsafe_allow_html=True)

    default_corpus = os.path.abspath("test_corpus")
    current_target = st.session_state.get("scan_path", default_corpus)

    # 1. Target Selection Zone
    st.markdown("""
    <div class="stitch-card-header">
        <div class="stitch-card-title">
            <span class="material-symbols-outlined" style="color: #f59e0b; font-size: 16px;">folder_special</span>
            <span>1. Target Directory Selection</span>
        </div>
        <div class="stitch-card-sub">Air-Gapped Sandbox</div>
    </div>
    """, unsafe_allow_html=True)

    col_target1, col_target2 = st.columns([3, 1])
    with col_target1:
        path_input = st.text_input("Target Directory / Repository Path", value=current_target, key="new_scan_path_input")
        st.session_state["scan_path"] = path_input

    with col_target2:
        use_corpus = st.checkbox("Use Bundled Test Corpus", value=("test_corpus" in path_input), key="chk_use_corpus")
        if use_corpus:
            st.session_state["scan_path"] = default_corpus
            path_input = default_corpus

    # File count telemetry
    if os.path.exists(path_input):
        file_count = sum([len(files) for r, d, files in os.walk(path_input) if not any(x in r for x in ('.git', 'node_modules', 'venv', '__pycache__'))])
        st.markdown(f"""
        <div style="font-family: 'JetBrains Mono'; font-size: 11px; color: #94a3b8; margin-top: -6px; margin-bottom: 12px;">
            Target Verified: <span style="color: #6de575;">{path_input}</span> · {file_count} files queued for discovery
        </div>
        """, unsafe_allow_html=True)
    else:
        st.warning(f"Target path does not exist on disk: {path_input}")

    # 2. Collector Modules Selector
    st.markdown("""
    <div class="stitch-card-header" style="margin-top: 14px;">
        <div class="stitch-card-title">
            <span class="material-symbols-outlined" style="color: #38bdf8; font-size: 16px;">tune</span>
            <span>2. Cryptographic Discovery Collectors</span>
        </div>
        <div class="stitch-card-sub">Select Enabled Engines</div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.checkbox("Source AST Scanner (Python Call-Site Visitor & Java Parser)", value=True, disabled=True,
                    help="Parses AST syntax trees and extracts cryptographic parameters, key sizes, modes, and padding.")
        st.checkbox("Manifest Dependency Scanner (requirements.txt, pom.xml, package.json, go.mod)", value=True, disabled=True,
                    help="Discovers cryptographic libraries and indirect algorithmic dependencies across ecosystems.")
        st.checkbox("Certificate & Public Key Scanner (X.509 PEM, DER, PKCS#12, OpenSSH)", value=True, disabled=True,
                    help="Inspects certificates, public keys, and cryptographic agility without private key extraction.")

    with c2:
        st.checkbox("Configuration & Cipher Suite Scanner (nginx.conf, sshd_config, openssl.cnf)", value=True, disabled=True,
                    help="Extracts TLS protocol bounds and cipher suite declarations.")
        st.checkbox("JVM Bytecode Constant Pool Scanner (.class, .jar archives)", value=True, disabled=True,
                    help="Pure-Python JVM constant pool extractor with zip-slip safety.")
        st.checkbox("Live Endpoints & Container Scans (Planned / Enterprise Roadmap)", value=False, disabled=True,
                    help="Roadmap capability. ECDAT strictly focuses on verified air-gapped static discovery in MVP.")

    # 3. Execution Action & Live Progress
    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    if st.button("🚀 Initiate Cryptographic Discovery & AST Scan", type="primary", use_container_width=True):
        if not os.path.exists(path_input):
            st.error(f"Cannot run scan: directory '{path_input}' does not exist.")
            return

        progress_container = st.container()
        with progress_container:
            prog_bar = st.progress(0.0)
            status_text = st.empty()
            log_preview = st.empty()

            stages = [
                ("DISCOVERY", "Discovering AST cryptographic usages in source code...", 0.15),
                ("DEPENDENCIES", "Parsing package manifests and dependency trees...", 0.30),
                ("CERTIFICATES", "Inspecting X.509, PKCS#12, and OpenSSH public keys...", 0.45),
                ("CONFIGURATION", "Scanning TLS cipher suites and cryptographic configurations...", 0.60),
                ("NORMALIZATION", "Deduplicating and normalizing cryptographic assets...", 0.70),
                ("QUANTUM ANALYSIS", "Applying Shor & Grover vulnerability categorization...", 0.80),
                ("MOSCA", "Evaluating Mosca inequality (X + Y > Z) and HNDL / TNFL risks...", 0.90),
                ("CBOM", "Generating CycloneDX 1.6 CBOM and verifying official JSON schema...", 0.98),
            ]

            collected_logs = st.session_state.get("scan_logs", [])

            def _on_log(level, msg):
                t_str = time.strftime("%H:%M:%S")
                collected_logs.append((t_str, level, msg))
                st.session_state["scan_logs"] = collected_logs

            for stage_name, stage_desc, frac in stages:
                status_text.markdown(f"**Stage:** `{stage_name}` — {stage_desc}")
                prog_bar.progress(frac)
                time.sleep(0.05)

            try:
                assets, metrics = scan_executor_fn(path_input, log_callback=_on_log)
                prog_bar.progress(1.0)
                status_text.success(f"✓ Scan completed successfully: {metrics['total_assets']} cryptographic assets identified in {metrics['scan_time_s']}s")
                time.sleep(0.4)
                navigate_fn("Dashboard")
            except Exception as e:
                st.error(f"Scan pipeline error: {e}")
