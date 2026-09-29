# Enterprise Cryptographic Discovery & Analysis Tool (ECDAT)
**SIH 2026 | PS ID: 26164 | NTRO**  
**Theme:** Blockchain & Cybersecurity | **Software Edition**  
**Version:** 1.0 (Stable Final Integration Build)  

---

## 🛡️ 1. What ECDAT Does

ECDAT is an air-gapped, zero-telemetry cybersecurity and Post-Quantum Cryptography (PQC) readiness tool designed for critical enterprise infrastructure. It enables organizations to:

1. **Discover Cryptographic Assets:** Automatically scan multi-language source code, package manifests, X.509 digital certificates, keystores, network server configurations, and compiled Java bytecode.
2. **Standardize into a Cryptographic Bill of Materials (CBOM):** Generate an official CycloneDX 1.6 CBOM and validate it in-memory against the official JSON schema with **0 errors**.
3. **Classify Post-Quantum Vulnerability:** Accurately categorize assets into Shor-broken (CRQC vulnerable), Grover-weakened (symmetric security halved), Classically-broken (legacy algorithms like MD5/SHA-1/DES), and Quantum-safe.
4. **Evaluate Threat Surface (HNDL / TNFL):** Distinguish between Harvest-Now-Decrypt-Later (confidentiality) and Trust-Now-Forge-Later (authenticity/signatures).
5. **Simulate Mosca's Inequality:** Interactively model $X + Y > Z$ (Data Lifetime + Migration Time vs CRQC Arrival Horizon).
6. **Prioritize Explainable Risk:** Calculate deterministic 0–100 risk scores based on the NTRO 5-factor model without black-box metrics.
7. **Deliver Actionable Migration Guidance:** Map vulnerable primitives to NIST FIPS 203 (ML-KEM), FIPS 204 (ML-DSA), FIPS 205 (SLH-DSA), and hybrid transitional standards.
8. **Export Multi-Format Deliverables:** Produce CBOM JSON, SARIF 2.1.0 (for GitHub / IDE code scanning), Executive HTML Reports, ReportLab A4 PDF reports, CSV inventories, and Markdown summaries.

---

## 🏛️ 2. Architecture & Pipeline

```text
PROJECT SOURCE ROOT / ARTIFACTS
       │
       ├── Source Code (.py, .js, .java, .ts) ──► Python AST Visitor + Regex Fallback
       ├── Manifests (requirements, pom, etc.) ──► Multi-Ecosystem Parsers (PyPI, Maven, npm, Go, Cargo)
       ├── Certificates (.pem, .der, .p12, .pub) ─► X.509 (PEM/DER) + PKCS#12 + OpenSSH Public Keys
       ├── Server Configs (nginx, openssl, etc.) ─► TLS Protocol & Cipher Suite Parsers
       └── Java Bytecode (.class, .jar) ─────────► Offline Constant Pool Reader (0xCAFEBABE)
                                │
                                ▼
                RAW FORENSIC EVIDENCE & NORMALIZATION
                (File, Line, Rule ID, Snippet, Provenance: OBSERVED)
                                │
                                ▼
                CROSS-SCANNER DEDUPLICATION
                (Key: [NormPath, Line, Algo, Usage] with Confidence Upgrade)
                                │
                                ▼
                POST-QUANTUM CLASSIFICATION & HNDL/TNFL
                (Shor-Broken, Grover-Weakened, Legacy, Quantum-Safe)
                                │
                                ▼
                MOSCA LIFETIME MODEL (X + Y > Z)
                                │
                                ▼
                EXPLAINABLE RISK ENGINE (NTRO FORMULA)
                                │
                                ▼
                PQC RECOMMENDATIONS (NIST FIPS 203/204/205)
                                │
                                ▼
                CYCLONEDX 1.6 CBOM SERIALIZATION & SCHEMA VALIDATION
                                │
                ┌───────────────┴───────────────┐
                ▼                               ▼
    MULTI-FORMAT DELIVERABLES         STREAMLIT DASHBOARD
    (CBOM, SARIF, HTML, PDF, CSV)     (Interactive GUI & Simulator)
```

---

## ⚙️ 3. Installation & Setup

### Prerequisites
- Python 3.10+ (Tested on Python 3.11, 3.12, and 3.14)
- Git

### Quick Setup (Local Environment)
```bash
# Clone the repository
git clone <repo-url>
cd SIH26164

# Create and activate virtual environment
python -m venv venv
# On Windows PowerShell:
.\venv\Scripts\Activate.ps1
# On Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

## 🚀 4. Running Locally

### 1. Launch the Interactive Dashboard
```bash
python run.py
# Or directly via streamlit:
streamlit run app/ui/dashboard.py
```
Open your browser at `http://localhost:8501`.

### 2. Run Headless / Command-Line Scan
To scan a target folder programmatically:
```python
from app.pipeline import run_full_scan
from app.cbom.cyclonedx import generate_cyclonedx_cbom, validate_cbom
from app.reports.reporter import generate_all_reports

assets, metrics = run_full_scan("test_corpus")
cbom = generate_cyclonedx_cbom(assets)
val = validate_cbom(cbom)
generate_all_reports(assets, metrics, val, "output")
```

---

## 📊 5. Supported Inputs & Manifests

| Category | Supported Formats | Scanner Implementation |
|---|---|---|
| **Python Source** | `.py` | AST Call-Site Visitor (`hashlib`, `RSA.generate`, `AES.new`) + Regex Fallback |
| **Java Source** | `.java` | Static Pattern Engine (`KeyPairGenerator`, `Cipher`, `Signature`, `MessageDigest`) |
| **JavaScript / TypeScript** | `.js`, `.ts`, `.jsx`, `.tsx` | WebCrypto and Node.js `crypto` API indicators (`createCipheriv`, `createHash`) |
| **Dependency Manifests** | `requirements.txt`, `pyproject.toml`, `pom.xml`, `package.json`, `package-lock.json`, `go.mod`, `Cargo.toml` | Offline manifest parsers with `defusedxml` protection |
| **Digital Certificates** | `.pem`, `.crt`, `.cer`, `.der` | Full X.509 metadata extraction (Algorithm, Key Size, Subject, Issuer, Validity) |
| **Keystores & Public Keys**| `.p12`, `.pfx`, `.pub` | PKCS#12 bundle parser & OpenSSH public key loader (**Zero private key storage**) |
| **Configuration Files** | `nginx.conf`, `sshd_config`, `openssl.cnf`, `.conf`, `.cfg` | TLS protocols, SSL cipher suites, DH parameter groups |
| **Java JVM Binaries** | `.class`, `.jar`, `.war` | Offline constant pool (`0xCAFEBABE`) static analyzer with Zip Slip containment |

---

## 📑 6. Reports & Deliverables

Every scan produces 6 standard deliverables in `output/` and `output/final_evidence/`:

1. **`cbom.json`**: CycloneDX 1.6 Cryptographic BOM strictly validated against `schemas/bom-1.6.schema.json`.
2. **`inventory.csv`**: Tabular asset inventory with rule IDs, locations, quantum status, and risk bands.
3. **`findings.sarif`**: Schema-valid SARIF 2.1.0 output for automated CI/CD code scanning.
4. **`report.html`**: Standalone, dark-palette executive security report with interactive metrics.
5. **`report.pdf`**: Printable executive risk report built via ReportLab 5.0.1.
6. **`summary.md`**: Executive markdown summary suitable for commit comments and release notes.

---

## 🧪 7. Automated Testing & Verification

Run the full automated acceptance and regression test suite:
```bash
python -m pytest tests/ -v
```

### Verified Results:
- **48 passed, 0 failed, 0 skipped** in 0.59 seconds.
- 100% Class Recall across planted algorithms on `test_corpus`.
- 0 Schema Errors during official CycloneDX 1.6 CBOM validation.

---

## 🔒 8. Security Controls & Air-Gap Guarantee

- **Air-Gapped Operation:** No outbound HTTP/HTTPS calls during discovery or analysis.
- **Private Key Immunity:** Scanners never persist, serialize, or log private key bytes.
- **Zip Slip & Archive Bomb Guard:** JAR and archive readers enforce strict relative path resolution and cap entry extraction (max 10MB per class, max 2000 entries per archive).
- **XML Entity Defense:** Uses `defusedxml` to block XML external entity (XXE) and billion-laughs attacks.

---

## ⚠️ 9. Limitations & Roadmap

### Documented Limitations
- **Container Scanning:** Scans `.class` and `.jar` binaries and Dockerfiles offline; scanning live layered OCI containers without a container runtime daemon is on the roadmap.
- **Live Network PCAP:** Designed for static application source analysis; passive live network PCAP sniffing is out of scope for the static core.

### Future Roadmap
- Integration with live container registries via secure read-only image tarballs.
- Extended AST support for C/C++ crypto call-sites.

---

## 🎬 10. Reproducible Demonstration Workflow

To demonstrate ECDAT for judges in 60 seconds:
1. Run `python run.py` (opens Dashboard).
2. Go to **New Scan**, select `test_corpus` (or `test-data/sample-project`), and click **Start Cryptographic Scan**.
3. Show the **Executive Dashboard**: observe Shor-broken assets, HNDL confidentiality risks, and Mosca violations.
4. Go to **Inventory**: click on any finding (e.g. `RSA-2048`) to view forensic evidence (file, line number, source snippet, deterministic rule ID `ECDAT-SRC-RSA-001`, and PQC recommendation `ML-KEM-768`).
5. Go to **Mosca Simulator**: move the CRQC horizon slider (e.g., from 2035 to 2030) and demonstrate dynamic risk score re-computation.
6. Go to **Reports**: demonstrate the **Official Schema Validation: PASS ✓ (0 Errors)** badge and download the deliverables (`cbom.json`, `findings.sarif`, `report.html`, `report.pdf`).
