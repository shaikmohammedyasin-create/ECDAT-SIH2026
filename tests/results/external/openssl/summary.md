# ECDAT Executive Scan Summary
**Timestamp:** 2026-09-30 02:16:04 UTC  
**CycloneDX 1.6 CBOM Status:** VALID (0 Errors)  

## Key Scan Metrics
- **Total Cryptographic Assets:** 1295
- **Shor-Broken (Asymmetric):** 454
- **Grover-Weakened (Symmetric):** 136
- **Classically Broken (Legacy):** 56
- **Mosca Violations (X + Y > Z):** 590
- **Critical Risk Assets:** 629
- **High Risk Assets:** 17

## Top Findings
| Rule ID | Algorithm | Quantum Class | Risk Band | Location | Recommendation |
|---|---|---|---|---|---|
| `ECDAT-CERT-PEM-001` | RSA | SHOR_BROKEN | Critical (93.0) | `client.pem:1` | ML-DSA-65 |
| `ECDAT-CERT-PEM-001` | DSA | SHOR_BROKEN | Critical (93.0) | `dsa-ca.pem:1` | ML-DSA-65 |
| `ECDAT-CERT-PEM-001` | DSA | SHOR_BROKEN | Critical (93.0) | `dsa-pca.pem:1` | ML-DSA-65 |
| `ECDAT-CERT-DER-001` | RSA | SHOR_BROKEN | Critical (93.0) | `insta.ca.crt:1` | ML-DSA-65 |
| `ECDAT-CERT-PEM-001` | RSA | SHOR_BROKEN | Critical (93.0) | `server.pem:1` | ML-DSA-65 |
| `ECDAT-CERT-PEM-001` | RSA | SHOR_BROKEN | Critical (93.0) | `server2.pem:1` | ML-DSA-65 |
| `ECDAT-CERT-PEM-001` | RSA | SHOR_BROKEN | Critical (93.0) | `intca.pem:1` | ML-DSA-65 |
| `ECDAT-CERT-PEM-001` | RSA | SHOR_BROKEN | Critical (93.0) | `root.pem:1` | ML-DSA-65 |
| `ECDAT-CERT-PEM-001` | ECDSA | SHOR_BROKEN | Critical (93.0) | `server-ec.pem:1` | ML-DSA-65 |
| `ECDAT-CERT-PEM-001` | RSA | SHOR_BROKEN | Critical (93.0) | `server.pem:1` | ML-DSA-65 |
| `ECDAT-CERT-PEM-001` | RSA | SHOR_BROKEN | Critical (93.0) | `cacert.pem:1` | ML-DSA-65 |
| `ECDAT-CERT-PEM-001` | RSA | SHOR_BROKEN | Critical (93.0) | `signer.pem:1` | ML-DSA-65 |
| `ECDAT-CERT-PEM-001` | RSA | SHOR_BROKEN | Critical (93.0) | `signer2.pem:1` | ML-DSA-65 |
| `ECDAT-CERT-PEM-001` | RSA | SHOR_BROKEN | Critical (93.0) | `rootcert.pem:1` | ML-DSA-65 |
| `ECDAT-CERT-PEM-001` | RSA | SHOR_BROKEN | Critical (93.0) | `servercert.pem:1` | ML-DSA-65 |
