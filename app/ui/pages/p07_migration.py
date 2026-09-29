"""
Screen 7: ECDAT - Post-Quantum Cryptography Migration Guidance.
Stitch Screen ID: 20778e5d24e74d94a4037eebecc601ce
"""
import os
import streamlit as st
import pandas as pd


def render(assets, navigate_fn):
    st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 16px; border-bottom: 1px solid #30353d; padding-bottom: 10px;">
        <div>
            <div style="display: flex; align-items: center; gap: 8px;">
                <h1 style="font-size: 20px; font-weight: 700; margin: 0; color: #dee2ec;">Deterministic Post-Quantum Migration Guidance</h1>
                <span class="stitch-badge" style="background-color: rgba(109, 229, 117, 0.15); color: #6de575; border: 1px solid rgba(109, 229, 117, 0.4);">
                    NIST FIPS 203 / 204 / 205 COMPLIANT
                </span>
            </div>
            <div style="font-size: 12px; color: #94a3b8; margin-top: 4px;">
                Deterministic transition roadmaps from classical and vulnerable primitives to post-quantum standards and hybrid schemes
            </div>
        </div>
        <div style="font-family: 'JetBrains Mono', monospace; font-size: 11px; color: #ffc174;">
            Standard Baseline: <span style="font-weight: 700;">NIST PQC Standards</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if not assets:
        st.info("ℹ️ No cryptographic assets loaded. Run a scan from the **New Scan** page first.")
        if st.button("Start New Scan →"):
            navigate_fn("New Scan")
        return

    # 1. NIST PQC Standards Reference Banner matching Stitch Screen 7
    st.markdown("""
    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-bottom: 16px;">
        <div class="stitch-card-lowest">
            <div style="font-family: 'JetBrains Mono'; font-weight: 700; font-size: 11px; color: #6de575;">NIST FIPS 203 (ML-KEM)</div>
            <div style="font-size: 11px; color: #94a3b8; margin-top: 2px;">
                Primary Key Encapsulation Mechanism (Module-Lattice KEM). Recommended replacement for RSA / ECDH key exchange.
            </div>
        </div>
        <div class="stitch-card-lowest">
            <div style="font-family: 'JetBrains Mono'; font-weight: 700; font-size: 11px; color: #38bdf8;">NIST FIPS 204 (ML-DSA)</div>
            <div style="font-size: 11px; color: #94a3b8; margin-top: 2px;">
                Primary Digital Signature Algorithm. Recommended replacement for RSA-PSS and ECDSA certificates & authentication.
            </div>
        </div>
        <div class="stitch-card-lowest">
            <div style="font-family: 'JetBrains Mono'; font-weight: 700; font-size: 11px; color: #ffc174;">NIST FIPS 205 (SLH-DSA)</div>
            <div style="font-size: 11px; color: #94a3b8; margin-top: 2px;">
                Stateless Hash-Based Digital Signatures. Fallback signature algorithm independent of lattice assumptions.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 2. Portfolio-Wide Migration Matrix
    st.markdown("""
    <div class="stitch-card-header">
        <div class="stitch-card-title">
            <span class="material-symbols-outlined" style="color: #6de575; font-size: 16px;">swap_calls</span>
            <span>Cryptographic Inventory Migration Matrix</span>
        </div>
        <div class="stitch-card-sub">Deterministic Action Plan</div>
    </div>
    """, unsafe_allow_html=True)

    rows = []
    seen = set()
    for a in sorted(assets, key=lambda x: x.risk_score, reverse=True):
        sig = (a.algorithm, a.usage.value)
        if sig not in seen and a.recommendation:
            seen.add(sig)
            target = a.recommendation.split(":")[-1].strip() if ":" in a.recommendation else a.recommendation
            strategy = "Hybrid Transition (Dual-Cert/KEM)" if a.hybrid_option else "Direct Primitive Replacement"
            rows.append({
                "Current Algorithm": a.algorithm,
                "Usage Primitive": a.usage.value,
                "Risk Band": a.risk_band,
                "Risk Score": round(a.risk_score, 1),
                "Recommended Target": target,
                "Migration Strategy": strategy,
                "Standard": a.standard or "NIST PQC",
                "Effort": a.migration_effort or "Moderate"
            })

    if rows:
        df_mig = pd.DataFrame(rows)
        st.dataframe(df_mig, use_container_width=True, hide_index=True)

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # 3. Detailed Cryptographic Family Roadmaps
    st.markdown("""
    <div class="stitch-card-header">
        <div class="stitch-card-title">
            <span class="material-symbols-outlined" style="color: #ffc174; font-size: 16px;">route</span>
            <span>Standard Transition Roadmaps by Cryptographic Family</span>
        </div>
        <div class="stitch-card-sub">Implementation Guidance</div>
    </div>
    """, unsafe_allow_html=True)

    t1, t2, t3, t4 = st.tabs([
        "Asymmetric Key Exchange (KEM)",
        "Digital Signatures & PKI",
        "Symmetric Ciphers",
        "Cryptographic Hashes"
    ])

    with t1:
        st.markdown("""
        <div style="padding: 6px 0; font-size: 12px; line-height: 1.6; color: #dee2ec;">
            <div style="font-weight: 700; color: #ffb4ab; margin-bottom: 6px;">Vulnerable: RSA Key Exchange, Diffie-Hellman (DH/ECDH), X25519</div>
            <div style="color: #94a3b8; margin-bottom: 8px;">
                Asymmetric key exchange algorithms are broken by Shor's algorithm on a quantum computer. Attackers can perform Harvest-Now-Decrypt-Later (HNDL).
            </div>
            <div style="background-color: #171c23; border: 1px solid #30353d; padding: 10px; border-radius: 3px; font-family: 'JetBrains Mono'; font-size: 11px;">
                <strong>Recommended Target:</strong> ML-KEM-768 (NIST FIPS 203)<br>
                <strong>Hybrid Transition Option:</strong> X25519 + ML-KEM-768 (Combines classical ECDH security with post-quantum security)<br>
                <strong>Standards Reference:</strong> NIST SP 800-56C Rev 2, IETF TLS 1.3 Hybrid Key Exchange Draft
            </div>
        </div>
        """, unsafe_allow_html=True)

    with t2:
        st.markdown("""
        <div style="padding: 6px 0; font-size: 12px; line-height: 1.6; color: #dee2ec;">
            <div style="font-weight: 700; color: #ffb4ab; margin-bottom: 6px;">Vulnerable: RSA Signatures (PKCS#1 v1.5 / PSS), ECDSA, Ed25519</div>
            <div style="color: #94a3b8; margin-bottom: 8px;">
                Digital signatures are broken by Shor's algorithm. Attackers can forge signatures and invalidate authentication, code-signing, and certificates (TNFL).
            </div>
            <div style="background-color: #171c23; border: 1px solid #30353d; padding: 10px; border-radius: 3px; font-family: 'JetBrains Mono'; font-size: 11px;">
                <strong>Primary Target:</strong> ML-DSA-65 (NIST FIPS 204)<br>
                <strong>Alternative Stateless Target:</strong> SLH-DSA-SHA2-128s (NIST FIPS 205)<br>
                <strong>Migration Strategy:</strong> Composite X.509 dual-signature certificates for backward-compatible PKI enrollment
            </div>
        </div>
        """, unsafe_allow_html=True)

    with t3:
        st.markdown("""
        <div style="padding: 6px 0; font-size: 12px; line-height: 1.6; color: #dee2ec;">
            <div style="font-weight: 700; color: #f59e0b; margin-bottom: 6px;">Weakened: AES-128, 3DES, Blowfish</div>
            <div style="color: #94a3b8; margin-bottom: 8px;">
                Grover's search algorithm squares the speed of brute-force attacks against symmetric ciphers, halving the effective key security (AES-128 → 64-bit security). 3DES is classically broken.
            </div>
            <div style="background-color: #171c23; border: 1px solid #30353d; padding: 10px; border-radius: 3px; font-family: 'JetBrains Mono'; font-size: 11px;">
                <strong>Recommended Target:</strong> AES-256-GCM (Provides 128-bit quantum security margin against Grover's algorithm)<br>
                <strong>Action:</strong> Upgrade key generation routines to 256 bits; eliminate 64-bit block ciphers (3DES/DES) immediately
            </div>
        </div>
        """, unsafe_allow_html=True)

    with t4:
        st.markdown("""
        <div style="padding: 6px 0; font-size: 12px; line-height: 1.6; color: #dee2ec;">
            <div style="font-weight: 700; color: #ef4444; margin-bottom: 6px;">Classically Broken: MD5, SHA-1</div>
            <div style="color: #94a3b8; margin-bottom: 8px;">
                MD5 and SHA-1 have known practical collision attacks (SHAttered, Flame). Immediate hygiene risk independent of quantum computing.
            </div>
            <div style="background-color: #171c23; border: 1px solid #30353d; padding: 10px; border-radius: 3px; font-family: 'JetBrains Mono'; font-size: 11px;">
                <strong>Recommended Target:</strong> SHA-256 or SHA-3 (FIPS 180-4 / FIPS 202)<br>
                <strong>Action:</strong> Replace all hashing, checksum, and HMAC routines; reject certificates signed with SHA-1
            </div>
        </div>
        """, unsafe_allow_html=True)
