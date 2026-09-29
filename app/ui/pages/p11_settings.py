"""
Screen 10 / 11: ECDAT - Settings & Security Policies.
Stitch Screen ID: 6648b8bb66404c01bb2935da463f952f
"""
import streamlit as st


def render(navigate_fn):
    st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 16px; border-bottom: 1px solid #30353d; padding-bottom: 10px;">
        <div>
            <div style="display: flex; align-items: center; gap: 8px;">
                <h1 style="font-size: 20px; font-weight: 700; margin: 0; color: #dee2ec;">Settings & Security Policies</h1>
                <span class="stitch-badge" style="background-color: rgba(245, 158, 11, 0.15); color: #ffc174; border: 1px solid rgba(245, 158, 11, 0.4);">
                    LOCAL AIR-GAP CONFIG
                </span>
            </div>
            <div style="font-size: 12px; color: #94a3b8; margin-top: 4px;">
                Cryptographic detection parameters, deterministic risk model thresholds, and air-gapped security assurances
            </div>
        </div>
        <div style="font-family: 'JetBrains Mono', monospace; font-size: 11px; color: #6de575;">
            Zero Egress: <span style="font-weight: 700;">ENFORCED</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns([1, 1])

    with c1:
        # 1. Scanner Engine Parameters
        st.markdown("""
        <div class="stitch-card-header">
            <div class="stitch-card-title">
                <span class="material-symbols-outlined" style="color: #38bdf8; font-size: 16px;">tune</span>
                <span>Cryptographic Discovery Engine</span>
            </div>
            <div class="stitch-card-sub">Static AST & Regex</div>
        </div>
        """, unsafe_allow_html=True)

        st.text_input("Ignore Paths (Comma-separated)", value=".git, node_modules, venv, __pycache__, dist, build", disabled=True)
        st.checkbox("Enable AST Call-Site Visitor (Python AST & Java Parser)", value=True, disabled=True)
        st.checkbox("Enable Pure-Python JVM Bytecode Constant Pool Scanner", value=True, disabled=True)
        st.checkbox("Enable Comment Filtering (Ignore commented-out ciphers)", value=True, disabled=True)
        st.checkbox("Strict Path Traversal & Zip-Slip Protection", value=True, disabled=True)

        # 2. Risk Model Thresholds
        st.markdown("""
        <div class="stitch-card-header" style="margin-top: 14px;">
            <div class="stitch-card-title">
                <span class="material-symbols-outlined" style="color: #f59e0b; font-size: 16px;">analytics</span>
                <span>Deterministic Risk Band Thresholds</span>
            </div>
            <div class="stitch-card-sub">0–100 Scale</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <table style="width: 100%; font-family: 'JetBrains Mono'; font-size: 11px; border-collapse: collapse;">
            <tr style="border-bottom: 1px solid #30353d;"><td style="color: #ef4444; padding: 4px 0;">CRITICAL:</td><td style="color: #dee2ec;">Score ≥ 80.0 (Immediate transition required)</td></tr>
            <tr style="border-bottom: 1px solid #30353d;"><td style="color: #f97316; padding: 4px 0;">HIGH:</td><td style="color: #dee2ec;">60.0 ≤ Score &lt; 80.0 (Near-term migration roadmap)</td></tr>
            <tr style="border-bottom: 1px solid #30353d;"><td style="color: #f59e0b; padding: 4px 0;">MEDIUM:</td><td style="color: #dee2ec;">40.0 ≤ Score &lt; 60.0 (Scheduled deprecation)</td></tr>
            <tr style="border-bottom: 1px solid #30353d;"><td style="color: #10b981; padding: 4px 0;">LOW:</td><td style="color: #dee2ec;">Score &lt; 40.0 (Monitored / Quantum-safe)</td></tr>
        </table>
        """, unsafe_allow_html=True)

    with c2:
        # 3. Security & Air-Gap Assurances
        st.markdown("""
        <div class="stitch-card-header">
            <div class="stitch-card-title">
                <span class="material-symbols-outlined" style="color: #6de575; font-size: 16px;">verified_user</span>
                <span>Air-Gap Security Policies</span>
            </div>
            <div class="stitch-card-sub">NTRO PS-ID 26164 Assurances</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div style="background-color: #171c23; border: 1px solid #30353d; border-radius: 4px; padding: 12px; margin-bottom: 14px; font-size: 11px; line-height: 1.6; color: #dee2ec;">
            <div style="font-weight: 700; color: #6de575; font-family: 'JetBrains Mono'; margin-bottom: 6px;">
                🔒 ZERO EXTERNAL NETWORK TRANSMISSION
            </div>
            All source code analysis, AST parsing, certificate validation, and CBOM generation occurs entirely inside this local process. 
            No source code, tokens, or artifacts are ever transmitted to third parties or remote cloud endpoints.
            <div style="font-weight: 700; color: #ffc174; font-family: 'JetBrains Mono'; margin-top: 10px; margin-bottom: 6px;">
                🔑 ZERO PRIVATE KEY PERSISTENCE
            </div>
            Private keys encountered in PEM or PKCS#12 bundles are inspected in ephemeral memory exclusively to determine algorithm family and key size. 
            Private key byte sequences are <strong>never persisted to CBOM JSON, reports, or disk logs</strong>.
            <div style="font-weight: 700; color: #38bdf8; font-family: 'JetBrains Mono'; margin-top: 10px; margin-bottom: 6px;">
                🛡️ STRICT PATH CONTAINMENT
            </div>
            Scans are strictly contained within the targeted directory boundaries with path sanitization preventing symlink or relative path traversal attacks.
        </div>
        """, unsafe_allow_html=True)

        # 4. About ECDAT Workstation
        st.markdown("""
        <div class="stitch-card-header">
            <div class="stitch-card-title">
                <span class="material-symbols-outlined" style="color: #ffc174; font-size: 16px;">info</span>
                <span>About ECDAT Workstation</span>
            </div>
            <div class="stitch-card-sub">Engineering Metadata</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div style="font-family: 'JetBrains Mono'; font-size: 11px; color: #94a3b8; line-height: 1.6;">
            <strong>Project:</strong> Enterprise Cryptographic Discovery & Analysis Tool (ECDAT)<br>
            <strong>Problem Statement:</strong> SIH 2026 PS ID 26164 (NTRO)<br>
            <strong>Version:</strong> v2.4 (Security Workstation Release)<br>
            <strong>Format Compliance:</strong> CycloneDX 1.6 CBOM, SARIF 2.1.0, ReportLab PDF<br>
            <strong>Standards:</strong> NIST FIPS 203 (ML-KEM), FIPS 204 (ML-DSA), FIPS 205 (SLH-DSA)
        </div>
        """, unsafe_allow_html=True)
