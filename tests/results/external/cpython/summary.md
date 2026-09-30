# ECDAT Executive Scan Summary
**Timestamp:** 2026-09-30 04:32:48 UTC  
**CycloneDX 1.6 CBOM Status:** VALID (0 Errors)  

## Key Scan Metrics
- **Total Cryptographic Assets:** 45
- **Shor-Broken (Asymmetric):** 15
- **Grover-Weakened (Symmetric):** 0
- **Classically Broken (Legacy):** 20
- **Mosca Violations (X + Y > Z):** 15
- **Critical Risk Assets:** 35
- **High Risk Assets:** 0

## Top Findings
| Rule ID | Algorithm | Quantum Class | Risk Band | Location | Recommendation |
|---|---|---|---|---|---|
| `ECDAT-CERT-PEM-001` | RSA | SHOR_BROKEN | Critical (93.0) | `allsans.pem:1` | ML-DSA-65 |
| `ECDAT-CERT-PEM-001` | RSA | SHOR_BROKEN | Critical (93.0) | `idnsans.pem:1` | ML-DSA-65 |
| `ECDAT-CERT-PEM-001` | RSA | SHOR_BROKEN | Critical (93.0) | `keycert.passwd.pem:1` | ML-DSA-65 |
| `ECDAT-CERT-PEM-001` | RSA | SHOR_BROKEN | Critical (93.0) | `keycert.pem:1` | ML-DSA-65 |
| `ECDAT-CERT-PEM-001` | RSA | SHOR_BROKEN | Critical (93.0) | `keycert2.pem:1` | ML-DSA-65 |
| `ECDAT-CERT-PEM-001` | RSA | SHOR_BROKEN | Critical (93.0) | `keycert3.pem:1` | ML-DSA-65 |
| `ECDAT-CERT-PEM-001` | RSA | SHOR_BROKEN | Critical (93.0) | `keycert4.pem:1` | ML-DSA-65 |
| `ECDAT-CERT-PEM-001` | ECDSA | SHOR_BROKEN | Critical (93.0) | `keycertecc.pem:1` | ML-DSA-65 |
| `ECDAT-CERT-PEM-001` | RSA | SHOR_BROKEN | Critical (93.0) | `nokia.pem:1` | ML-DSA-65 |
| `ECDAT-CERT-PEM-001` | RSA | SHOR_BROKEN | Critical (93.0) | `nosan.pem:1` | ML-DSA-65 |
| `ECDAT-CERT-PEM-001` | RSA | SHOR_BROKEN | Critical (93.0) | `nullbytecert.pem:1` | ML-DSA-65 |
| `ECDAT-CERT-PEM-001` | RSA | SHOR_BROKEN | Critical (93.0) | `pycacert.pem:1` | ML-DSA-65 |
| `ECDAT-CERT-PEM-001` | RSA | SHOR_BROKEN | Critical (93.0) | `selfsigned_pythontestdotnet.pem:1` | ML-DSA-65 |
| `ECDAT-CERT-PEM-001` | RSA | SHOR_BROKEN | Critical (93.0) | `ssl_cert.pem:1` | ML-DSA-65 |
| `ECDAT-CERT-PEM-001` | RSA | SHOR_BROKEN | Critical (93.0) | `talos-2019-0758.pem:1` | ML-DSA-65 |
