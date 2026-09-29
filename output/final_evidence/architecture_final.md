# ECDAT Final Integrated Architecture Specification
**SIH 2026 | PS ID: 26164 | NTRO**  
**Enterprise Cryptographic Discovery & Analysis Tool (ECDAT)**  
**Version:** 1.0 Final Integration Build  
**Date:** September 30, 2026  

---

## 1. Complete Processing Pipeline

```
PROJECT SOURCE ROOT / ARTIFACTS
       │
       ├── Python Source (.py) ───────► AST Visitor + Regex Fallback ──┐
       ├── Java Source (.java) ───────► Regex & Call-Site Matching ────┤
       ├── JavaScript/TypeScript ─────► Node Crypto & WebCrypto Matched ┤
       ├── Manifests (pyproject, pom,─► Multi-Ecosystem Parser ────────┤
       │   package.json, go, cargo)                                    │
       ├── Certificates & Keys ───────► X.509 (PEM/DER) + PKCS#12 + ───┤
       │   (.pem, .crt, .der, .p12, .pub)   OpenSSH Public Keys        │
       ├── Configurations (.conf, tls)─► Directive & Cipher Suite Regex─┤
       └── Java JVM Binaries (.class, ─► Offline Constant Pool Parser ─┘
           .jar, .war)                  (Zip Slip & Bomb Protected)
                                       │
                                       ▼
                       RAW FINDING EXTRACTION & FORENSICS
                       (File, Line Number, Snippet, Rule ID,
                        Confidence, Provenance: OBSERVED)
                                       │
                                       ▼
                       CROSS-SCANNER DEDUPLICATION
                       (Tuple Key: [NormPath, Line, Algo, Usage])
                       (Prioritizes AST/High-Confidence/Exact Key Size)
                                       │
                                       ▼
                       QUANTUM VULNERABILITY CLASSIFICATION
                       ├── Shor-Broken (RSA, ECDSA, ECDH, DSA, X25519)
                       ├── Grover-Weakened (AES-128, AES-192, Unknown AES)
                       ├── Classically Broken (MD5, SHA-1, DES, 3DES, RC4)
                       └── Quantum-Safe (AES-256, SHA-256/384/512, ML-KEM/DSA)
                                       │
                                       ▼
                       HNDL & TNFL EXPOSURE TAGGING
                       ├── Confidentiality / Key Exchange ──► HNDL Risk
                       └── Authenticity / Signatures / Certs─► TNFL Risk
                                       │
                                       ▼
                       MOSCA THEOREM LIFETIME SIMULATION
                       Formula: Margin = Z - (X + Y)
                       ├── X: Data Protection Lifetime (Default: 10 yr)
                       ├── Y: Cryptographic Migration Time (Default: 3 yr)
                       └── Z: CRQC Horizon Parameter (Default: 2035)
                                       │
                                       ▼
                       EXPLAINABLE RISK ENGINE (NTRO FORMULATION)
                       Score = 100 × (
                           0.35 × QuantumExposure +
                           0.25 × BusinessCriticality +
                           0.15 × ExposureSurface +
                           0.15 × DataSensitivity +
                           0.10 × (1 - CryptoAgility)
                       )
                       Bands: Critical (≥75), High (≥50), Medium (≥25), Low (<25)
                                       │
                                       ▼
                       PQC MIGRATION RECOMMENDATION ENGINE
                       Deterministic NIST FIPS 203/204/205 Mappings
                       ├── KEX/PKE  ──► Hybrid X25519 + ML-KEM-768 or ML-KEM-768
                       ├── Signature──► ML-DSA-65 / SLH-DSA / LMS / XMSS
                       ├── Ciphers  ──► AES-256-GCM / ChaCha20-Poly1305
                       └── Hashes   ──► SHA-384 / SHA-512 / SHA-3
                                       │
                                       ▼
                       CYCLONEDX 1.6 CBOM SERIALIZATION
                       ├── UUIDv4 Dynamic Serial Number
                       ├── UTC ISO-8601 Timestamp
                       ├── Component Type: cryptographic-asset & library
                       ├── cryptoProperties: assetType, algorithmProperties,
                       │   certificateProperties, protocolProperties
                       └── Evidence: file occurrences, offset lines
                                       │
                                       ▼
                       OFFICIAL JSON SCHEMA VALIDATION
                       Target: schemas/bom-1.6.schema.json
                       Status: PASS (0 Errors)
                                       │
            ┌──────────────────────────┴──────────────────────────┐
            ▼                                                     ▼
MULTI-FORMAT DELIVERABLES                             STREAMLIT FORENSIC DASHBOARD
├── final_cbom.json                                   ├── Executive Dashboard
├── final_inventory.csv                               ├── Project Scanner
├── final_findings.sarif (SARIF 2.1.0)                ├── Live Cryptographic Inventory
├── final_report.html (Self-contained)                ├── Deep Forensic Asset Detail
├── final_report.pdf (ReportLab A4)                   ├── Interactive Mosca Simulator
└── summary.md (Executive Markdown)                   └── Deliverable Exports
```

---

## 2. Core Subsystems

### 2.1 Multi-Vector Discovery Engine
- **Source Scanner (`source_scanner.py`):**
  - AST Call-Site Visitor (`PythonCryptoASTVisitor`) inspecting `hashlib`, `pycryptodome` (`AES.new`, `RSA.generate`), and `cryptography` call nodes.
  - Pattern-based fallback for JavaScript, TypeScript, Java, and dynamic call sites.
- **Dependency Scanner (`dependency_scanner.py`):**
  - Manifest parsing across PyPI (`requirements.txt`, `pyproject.toml`), Maven (`pom.xml`), npm (`package.json`, `package-lock.json`), Go (`go.mod`), and Cargo (`Cargo.toml`).
  - Zero-telemetry, offline static analysis with `defusedxml` protection.
- **Certificate Scanner (`certificate_scanner.py`):**
  - Parses X.509 PEM and DER certificates, PKCS#12 bundles (`.p12`, `.pfx`), and OpenSSH public keys (`.pub`).
  - Strict security guarantee: Never extracts or persists private key material.
- **Configuration Scanner (`config_scanner.py`):**
  - Parses TLS protocol configurations, cipher suite suites, DH parameters, and SSL certificate directives.
  - Isolated comment-handling logic prevents comments from prematurely terminating directives.
- **JVM Binary Scanner (`binary_scanner.py`):**
  - Offline Java bytecode constant pool reader (`0xCAFEBABE`) extracting cryptographic classes and algorithms from `.class` and `.jar` archives.
  - Enforces Zip Slip path containment and archive bomb size limits (max 10MB per class, max 2000 entries per JAR).

### 2.2 Forensic Normalization & Evidence Model
- Every finding adheres to the unified `CryptoAsset` model:
  - Deterministic Rule IDs: `ECDAT-SRC-`, `ECDAT-CFG-`, `ECDAT-CERT-`, `ECDAT-DEP-`, `ECDAT-BIN-`.
  - Exact Location: `file_path`, `line_number`, and contextual source snippet.
  - Explicit Provenance Tracking: `OBSERVED` (directly extracted from scanned artifacts) vs `INFERRED` (calculated by recommendation/risk engines).

### 2.3 Post-Quantum Risk & Mosca Simulator
- **Quantum Rules (`quantum_rules.py`):**
  - Shor-Broken: Public-key algorithms vulnerable to Shor's algorithm on CRQC.
  - Grover-Weakened: Symmetric ciphers with effective security halved (including explicit uncertainty handling for unknown AES key lengths).
  - Classically-Broken: Legacy algorithms vulnerable to classical attacks (MD5, SHA-1, DES).
- **Threat Surface:**
  - HNDL (Harvest Now, Decrypt Later): Tagged on confidentiality and key exchange assets.
  - TNFL (Trust Now, Forge Later): Tagged on authenticity, signatures, and certificates.
- **Mosca Simulator (`mosca.py`):**
  - Interactive evaluation of $Z - (X + Y)$ with dynamic slider adjustment in the dashboard.

### 2.4 Risk Scoring Engine
- Implements the exact NTRO Source of Truth formulation:
  $$\text{Score} = 100 \times (0.35 \times Q + 0.25 \times B + 0.15 \times E + 0.15 \times S + 0.10 \times (1 - A))$$
  Where unknown enterprise metrics default to documented baseline assumptions (Data Sensitivity: Internal, Business Criticality: 3, Exposure: Internal).

### 2.5 CycloneDX 1.6 CBOM Serialization & Validation
- Emits schema-compliant CycloneDX 1.6 CBOM with dynamic UUIDv4 URNs and ISO-8601 UTC timestamps.
- Strictly validated in-memory against `schemas/bom-1.6.schema.json` via Draft 7 validator with **0 schema errors**.

### 2.6 Multi-Format Reporting Engine
- Dynamic generation of HTML (embedded dark cybersecurity styling), PDF (ReportLab A4 layout), SARIF 2.1.0 (GitHub / IDE code scanning compatible), CSV inventory, and Markdown summaries.
