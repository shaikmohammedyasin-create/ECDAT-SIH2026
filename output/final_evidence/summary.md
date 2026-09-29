# ECDAT Executive Scan Summary
**Timestamp:** 2026-09-29 19:01:24 UTC  
**CycloneDX 1.6 CBOM Status:** VALID (0 Errors)  

## Key Scan Metrics
- **Total Cryptographic Assets:** 32
- **Shor-Broken (Asymmetric):** 19
- **Grover-Weakened (Symmetric):** 4
- **Classically Broken (Legacy):** 6
- **Mosca Violations (X + Y > Z):** 23
- **Critical Risk Assets:** 21
- **High Risk Assets:** 8

## Top Findings
| Rule ID | Algorithm | Quantum Class | Risk Band | Location | Recommendation |
|---|---|---|---|---|---|
| `ECDAT-SRC-RSA-001` | RSA | SHOR_BROKEN | Critical (94.0) | `crypto_sample.py:17` | ML-KEM-768 + AES-256 envelope encryption |
| `ECDAT-CERT-PEM-001` | RSA | SHOR_BROKEN | Critical (93.0) | `test_cert.pem:1` | ML-DSA-65 |
| `ECDAT-SRC-RSA-GEN` | RSA | SHOR_BROKEN | Critical (87.8) | `CryptoSample.java:11` | ML-KEM-768 + AES-256 envelope encryption |
| `ECDAT-SRC-RSA-GEN` | RSA | SHOR_BROKEN | Critical (87.8) | `CryptoSample.java:12` | ML-KEM-768 + AES-256 envelope encryption |
| `ECDAT-SRC-RSA-GEN` | RSA | SHOR_BROKEN | Critical (87.8) | `CryptoSample.java:13` | ML-KEM-768 + AES-256 envelope encryption |
| `ECDAT-SRC-JAVA-DSA-001` | DSA | SHOR_BROKEN | Critical (87.8) | `CryptoSample.java:20` | ML-DSA-65 |
| `ECDAT-SRC-RSA-GEN` | RSA | SHOR_BROKEN | Critical (87.8) | `crypto_sample.py:4` | ML-KEM-768 + AES-256 envelope encryption |
| `ECDAT-SRC-ECDSA-GEN` | ECDSA | SHOR_BROKEN | Critical (87.8) | `crypto_sample.py:4` | ML-DSA-65 |
| `ECDAT-SRC-RSA-GEN` | RSA | SHOR_BROKEN | Critical (87.8) | `crypto_sample.py:8` | ML-KEM-768 + AES-256 envelope encryption |
| `ECDAT-SRC-RSA-GEN` | RSA | SHOR_BROKEN | Critical (87.8) | `crypto_sample.py:15` | ML-KEM-768 + AES-256 envelope encryption |
| `ECDAT-SRC-RSA-GEN` | RSA | SHOR_BROKEN | Critical (87.8) | `crypto_sample.py:16` | ML-KEM-768 + AES-256 envelope encryption |
| `ECDAT-SRC-ECDSA-GEN` | ECDSA | SHOR_BROKEN | Critical (87.8) | `crypto_sample.py:21` | ML-DSA-65 |
| `ECDAT-SRC-PY-EC-001` | ECDSA | SHOR_BROKEN | Critical (87.8) | `crypto_sample.py:23` | ML-DSA-65 |
| `ECDAT-SRC-JAVA-AES-001` | AES | GROVER_WEAKENED | Critical (84.2) | `CryptoSample.java:28` | AES-256-GCM |
| `ECDAT-SRC-AES-001` | AES | GROVER_WEAKENED | Critical (84.2) | `crypto_sample.py:29` | AES-256-GCM |
