# ECDAT Executive Scan Summary
**Timestamp:** 2026-09-30 02:17:36 UTC  
**CycloneDX 1.6 CBOM Status:** VALID (0 Errors)  

## Key Scan Metrics
- **Total Cryptographic Assets:** 205
- **Shor-Broken (Asymmetric):** 180
- **Grover-Weakened (Symmetric):** 11
- **Classically Broken (Legacy):** 2
- **Mosca Violations (X + Y > Z):** 191
- **Critical Risk Assets:** 193
- **High Risk Assets:** 0

## Top Findings
| Rule ID | Algorithm | Quantum Class | Risk Band | Location | Recommendation |
|---|---|---|---|---|---|
| `ECDAT-SRC-SSH-RSA-001` | RSA | SHOR_BROKEN | Critical (87.8) | `authfd.c:392` | ML-DSA-65 |
| `ECDAT-SRC-SSH-RSA-001` | RSA | SHOR_BROKEN | Critical (87.8) | `authfd.c:393` | ML-DSA-65 |
| `ECDAT-SRC-SSH-RSA-001` | RSA | SHOR_BROKEN | Critical (87.8) | `authfd.c:395` | ML-DSA-65 |
| `ECDAT-SRC-SSH-RSA-001` | RSA | SHOR_BROKEN | Critical (87.8) | `authfd.c:396` | ML-DSA-65 |
| `ECDAT-SRC-SSH-RSA-001` | RSA | SHOR_BROKEN | Critical (87.8) | `clientloop.c:2457` | ML-DSA-65 |
| `ECDAT-SRC-SSH-RSA-001` | RSA | SHOR_BROKEN | Critical (87.8) | `clientloop.c:2458` | ML-DSA-65 |
| `ECDAT-SRC-SSH-X25519-001` | X25519 | SHOR_BROKEN | Critical (87.8) | `compat.c:151` | Hybrid X25519 + ML-KEM-768 |
| `ECDAT-SRC-SSH-RSA-001` | RSA | SHOR_BROKEN | Critical (87.8) | `kex.c:1226` | ML-DSA-65 |
| `ECDAT-SRC-SSH-RSA-001` | RSA | SHOR_BROKEN | Critical (87.8) | `kex.c:1229` | ML-DSA-65 |
| `ECDAT-SRC-SSH-X25519-001` | X25519 | SHOR_BROKEN | Critical (87.8) | `myproposal.h:29` | Hybrid X25519 + ML-KEM-768 |
| `ECDAT-SRC-SSH-X25519-001` | X25519 | SHOR_BROKEN | Critical (87.8) | `myproposal.h:30` | Hybrid X25519 + ML-KEM-768 |
| `ECDAT-SRC-SSH-ED25519-001` | Ed25519 | SHOR_BROKEN | Critical (87.8) | `myproposal.h:42` | ML-DSA-65 |
| `ECDAT-SRC-SSH-ECDSA-001` | ECDSA | SHOR_BROKEN | Critical (87.8) | `myproposal.h:43` | ML-DSA-65 |
| `ECDAT-SRC-SSH-ECDSA-001` | ECDSA | SHOR_BROKEN | Critical (87.8) | `myproposal.h:44` | ML-DSA-65 |
| `ECDAT-SRC-SSH-ED25519-001` | Ed25519 | SHOR_BROKEN | Critical (87.8) | `myproposal.h:46` | ML-DSA-65 |
