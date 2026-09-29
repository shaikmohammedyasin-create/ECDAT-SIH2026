"""
Screen 4: ECDAT - Finding Inspector / Asset Detail.
Stitch Screen ID: 98b9e419d2fa4403b5ab7ebfeeca3307
"""
import os
import streamlit as st


def render(assets, navigate_fn):
    st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 16px; border-bottom: 1px solid #30353d; padding-bottom: 10px;">
        <div>
            <div style="display: flex; align-items: center; gap: 8px;">
                <h1 style="font-size: 20px; font-weight: 700; margin: 0; color: #dee2ec;">Finding Inspector</h1>
                <span class="stitch-badge" style="background-color: rgba(245, 158, 11, 0.15); color: #ffc174; border: 1px solid rgba(245, 158, 11, 0.4);">
                    FORENSIC ASSET DETAIL
                </span>
            </div>
            <div style="font-size: 12px; color: #94a3b8; margin-top: 4px;">
                Deep AST call-site evidence, parameter provenance, quantum threat categorization, and transition roadmap
            </div>
        </div>
        <div style="font-family: 'JetBrains Mono', monospace; font-size: 11px; color: #94a3b8;">
            SecOps Verification: <span style="color: #6de575;">AIR-GAP LOCAL</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if not assets:
        st.info("ℹ️ No assets available. Run a scan from the **New Scan** page first.")
        if st.button("Start New Scan →"):
            navigate_fn("New Scan")
        return

    # Select finding
    curr_idx = st.session_state.get("selected_asset_idx", 0)
    if curr_idx >= len(assets):
        curr_idx = 0

    options = {
        i: f"[{a.risk_band.upper()} {a.risk_score:.1f}] {a.rule_id or 'SRC'} · {a.algorithm}{'-' + str(a.key_size) if a.key_size else ''} ({a.usage.value}) — {os.path.basename(a.file_path)}:{a.line_number}"
        for i, a in enumerate(assets)
    }

    sel_col1, sel_col2 = st.columns([4, 1])
    with sel_col1:
        sel = st.selectbox("Select Cryptographic Asset to Inspect", list(options.keys()), index=curr_idx, format_func=lambda i: options[i])
        st.session_state["selected_asset_idx"] = sel
    with sel_col2:
        if st.button("← Back to Inventory", use_container_width=True):
            navigate_fn("Crypto Inventory")

    a = assets[sel]
    band_cls = "badge-critical" if a.risk_band == "Critical" else ("badge-high" if a.risk_band == "High" else "badge-med")

    # Header Badges Bar matching Stitch Screen 4
    threat_pill = ""
    if a.hndl_risk:
        threat_pill = '<span class="stitch-badge badge-hndl" style="margin-right: 6px;">THREAT: HNDL (Harvest Now Decrypt Later)</span>'
    elif a.tnfl_risk:
        threat_pill = '<span class="stitch-badge badge-tnfl" style="margin-right: 6px;">THREAT: TNFL (Trust Now Forge Later)</span>'

    q_cls = "badge-shor" if a.quantum_status.value == "Vulnerable" else ("badge-grover" if a.quantum_status.value == "Weakened" else "badge-safe")

    st.markdown(f"""
    <div style="background-color: #171c23; border: 1px solid #30353d; border-radius: 4px; padding: 10px 14px; margin-bottom: 16px; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 8px;">
        <div style="display: flex; align-items: center; gap: 8px;">
            <span class="stitch-badge {band_cls}">RISK: {a.risk_score:.1f} ({a.risk_band.upper()})</span>
            <span class="stitch-badge" style="background-color: #1b2027; color: #ffc174; border: 1px solid #f59e0b;">RULE: {a.rule_id or 'ECDAT-SRC'}</span>
            <span class="stitch-badge {q_cls}">QUANTUM: {a.quantum_status.value.upper()}</span>
            {threat_pill}
        </div>
        <div style="font-family: 'JetBrains Mono'; font-size: 11px; color: #94a3b8;">
            Confidence: <span style="color: #6de575; font-weight: 700;">{a.confidence}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Quick Inter-page Navigation Toolbar
    col_act1, col_act2, col_act3, col_act4 = st.columns(4)
    with col_act1:
        if st.button("⏳ Simulate in Mosca", use_container_width=True):
            navigate_fn("Mosca Simulator")
    with col_act2:
        if st.button("🔀 Migration Guidance", use_container_width=True):
            navigate_fn("Migration Guidance")
    with col_act3:
        if st.button("📈 Risk Factor Analysis", use_container_width=True):
            navigate_fn("Risk Analysis")
    with col_act4:
        if st.button("🛡️ View CycloneDX CBOM", use_container_width=True):
            navigate_fn("CycloneDX 1.6 CBOM")

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    # 2-Column Forensic View matching Stitch Screen 4
    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.markdown("""
        <div class="stitch-card-header">
            <div class="stitch-card-title">
                <span class="material-symbols-outlined" style="color: #38bdf8; font-size: 16px;">code</span>
                <span>Forensic Call-Site Evidence & Provenance</span>
            </div>
            <div class="stitch-card-sub">Static Syntax AST</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style="font-family: 'JetBrains Mono'; font-size: 11px; color: #94a3b8; margin-bottom: 6px;">
            Location: <span style="color: #dee2ec;">{a.file_path}</span>:<span style="color: #ffc174;">{a.line_number}</span>
        </div>
        """, unsafe_allow_html=True)

        # Code viewer
        st.code(a.source_snippet or f"# [AST Occurrence]\n{a.algorithm} usage detected at line {a.line_number}",
                language="python" if a.file_path.endswith(".py") else "text")

        # Threat Description
        st.markdown("""
        <div class="stitch-card-header" style="margin-top: 14px;">
            <div class="stitch-card-title">
                <span class="material-symbols-outlined" style="color: #ef4444; font-size: 16px;">security</span>
                <span>Quantum Threat Analysis</span>
            </div>
            <div class="stitch-card-sub">Harvest-Now / Trust-Now</div>
        </div>
        """, unsafe_allow_html=True)

        if a.hndl_risk:
            st.markdown("""
            <div style="background-color: rgba(147, 0, 10, 0.15); border: 1px solid rgba(255, 180, 171, 0.3); border-radius: 3px; padding: 10px; margin-bottom: 8px;">
                <div style="color: #ffb4ab; font-weight: 700; font-size: 11px; font-family: 'JetBrains Mono';">🚨 HARVEST NOW, DECRYPT LATER (HNDL) ACTIVE</div>
                <div style="color: #dee2ec; font-size: 11px; margin-top: 4px; line-height: 1.4;">
                    Encrypted ciphertext or key exchanges transmitted today can be intercepted and stored by adversaries, then decrypted once a cryptographically relevant quantum computer (CRQC) becomes operational.
                </div>
            </div>
            """, unsafe_allow_html=True)
        elif a.tnfl_risk:
            st.markdown("""
            <div style="background-color: rgba(120, 53, 15, 0.15); border: 1px solid rgba(245, 158, 11, 0.3); border-radius: 3px; padding: 10px; margin-bottom: 8px;">
                <div style="color: #ffc174; font-weight: 700; font-size: 11px; font-family: 'JetBrains Mono';">🚨 TRUST NOW, FORGE LATER (TNFL) ACTIVE</div>
                <div style="color: #dee2ec; font-size: 11px; margin-top: 4px; line-height: 1.4;">
                    Digital signatures and PKI certificates valid today can be forged retroactively via Shor's algorithm, undermining non-repudiation and firmware integrity.
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background-color: rgba(6, 78, 59, 0.15); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 3px; padding: 10px;">
                <div style="color: #86efac; font-weight: 700; font-size: 11px; font-family: 'JetBrains Mono';">✅ NO IMMEDIATE HNDL / TNFL THREAT FLAG</div>
                <div style="color: #dee2ec; font-size: 11px; margin-top: 4px;">Asset does not exhibit vulnerable long-term key exchange or public-key signature exposure.</div>
            </div>
            """, unsafe_allow_html=True)

    with col_right:
        st.markdown("""
        <div class="stitch-card-header">
            <div class="stitch-card-title">
                <span class="material-symbols-outlined" style="color: #f59e0b; font-size: 16px;">tune</span>
                <span>Cryptographic Parameters & Metadata</span>
            </div>
            <div class="stitch-card-sub">CBOM Properties</div>
        </div>
        """, unsafe_allow_html=True)

        params_html = f"""
        <table style="width: 100%; font-family: 'JetBrains Mono'; font-size: 11px; border-collapse: collapse;">
            <tr style="border-bottom: 1px solid #30353d;"><td style="color: #94a3b8; padding: 4px 0;">Algorithm:</td><td style="color: #ffc174; font-weight: 700;">{a.algorithm}</td></tr>
            <tr style="border-bottom: 1px solid #30353d;"><td style="color: #94a3b8; padding: 4px 0;">Primitive:</td><td style="color: #dee2ec;">{a.primitive}</td></tr>
            <tr style="border-bottom: 1px solid #30353d;"><td style="color: #94a3b8; padding: 4px 0;">Key Size:</td><td style="color: #dee2ec;">{a.key_size or 'Unknown / Not specified'}</td></tr>
            <tr style="border-bottom: 1px solid #30353d;"><td style="color: #94a3b8; padding: 4px 0;">Mode / Padding:</td><td style="color: #dee2ec;">{a.mode or 'N/A'} / {a.padding or 'N/A'}</td></tr>
            <tr style="border-bottom: 1px solid #30353d;"><td style="color: #94a3b8; padding: 4px 0;">Usage Function:</td><td style="color: #dee2ec;">{a.usage.value}</td></tr>
            <tr style="border-bottom: 1px solid #30353d;"><td style="color: #94a3b8; padding: 4px 0;">Asset Classification:</td><td style="color: #dee2ec;">{a.asset_type.value}</td></tr>
            <tr style="border-bottom: 1px solid #30353d;"><td style="color: #94a3b8; padding: 4px 0;">Rule Identifier:</td><td style="color: #38bdf8;">{a.rule_id or 'N/A'}</td></tr>
        </table>
        """
        st.markdown(params_html, unsafe_allow_html=True)

        # Mosca status for this asset
        st.markdown("""
        <div class="stitch-card-header" style="margin-top: 14px;">
            <div class="stitch-card-title">
                <span class="material-symbols-outlined" style="color: #6de575; font-size: 16px;">timeline</span>
                <span>Mosca Theorem (X + Y > Z)</span>
            </div>
            <div class="stitch-card-sub">Margin: Z - (X + Y)</div>
        </div>
        """, unsafe_allow_html=True)

        margin_str = f"{a.mosca_margin:.1f} years" if a.mosca_margin is not None else "N/A"
        if a.mosca_at_risk:
            st.markdown(f"""
            <div style="background-color: rgba(147, 0, 10, 0.15); border: 1px solid rgba(255, 180, 171, 0.3); border-radius: 3px; padding: 8px 12px;">
                <div style="color: #ffb4ab; font-weight: 700; font-size: 11px; font-family: 'JetBrains Mono';">🚨 AT RISK — NEGATIVE SECURITY MARGIN ({margin_str})</div>
                <div style="color: #dee2ec; font-size: 11px; margin-top: 2px;">
                    Combined data lifetime X and migration time Y exceed the planning horizon Z.
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="background-color: rgba(6, 78, 59, 0.15); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 3px; padding: 8px 12px;">
                <div style="color: #86efac; font-weight: 700; font-size: 11px; font-family: 'JetBrains Mono';">✅ WITHIN WINDOW — POSITIVE MARGIN ({margin_str})</div>
            </div>
            """, unsafe_allow_html=True)

        # Deterministic PQC Recommendation
        st.markdown("""
        <div class="stitch-card-header" style="margin-top: 14px;">
            <div class="stitch-card-title">
                <span class="material-symbols-outlined" style="color: #ffc174; font-size: 16px;">swap_calls</span>
                <span>Deterministic PQC Recommendation</span>
            </div>
            <div class="stitch-card-sub">NIST Standardized</div>
        </div>
        """, unsafe_allow_html=True)

        st.info(f"**Recommended Action:** {a.recommendation or 'Maintain algorithm under continuous monitoring.'}")
        if a.hybrid_option:
            st.markdown(f"**Hybrid Migration Option:** `{a.hybrid_option}`")
        if a.standard:
            st.markdown(f"**Standard Specification:** `{a.standard}`")
        if a.migration_path:
            st.markdown("**Deterministic Transition Steps:**")
            for step in a.migration_path:
                st.markdown(f"- {step}")
