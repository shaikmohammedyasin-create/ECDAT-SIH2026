# Enterprise Cryptographic Discovery & Analysis Tool (ECDAT)
**SIH 2026 | PS ID: 26164 | NTRO**  
**Theme:** Blockchain & Cybersecurity | **Software Edition**  
**Version:** 2.0 (FastAPI Engine + Stitch React Workstation Build)  

---

## 🛡️ 1. What ECDAT Does

ECDAT is an air-gapped, zero-telemetry cybersecurity and Post-Quantum Cryptography (PQC) readiness tool designed for critical enterprise infrastructure. It enables defense and intelligence organizations to:

1. **Discover Cryptographic Assets:** Automatically scan multi-language source code (Python, Java, JS/TS), package manifests, X.509 digital certificates, keystores, network server configurations, and compiled Java bytecode.
2. **Standardize into a Cryptographic Bill of Materials (CBOM):** Generate an official CycloneDX 1.6 CBOM and validate it in-memory against the official JSON schema with **0 errors**.
3. **Classify Post-Quantum Vulnerability:** Accurately categorize assets into Shor-broken (CRQC vulnerable), Grover-weakened (symmetric security halved), Classically-broken (legacy algorithms like MD5/SHA-1/DES), and Quantum-safe.
4. **Evaluate Threat Surface (HNDL / TNFL):** Distinguish between Harvest-Now-Decrypt-Later (confidentiality) and Trust-Now-Forge-Later (authenticity/signatures).
5. **Simulate Mosca's Inequality:** Interactively model $X + Y > Z$ (Data Lifetime + Migration Time vs CRQC Arrival Horizon).
6. **Prioritize Explainable Risk:** Calculate deterministic 0–100 risk scores based on the NTRO 5-factor model without black-box metrics.
7. **Deliver Actionable Migration Guidance:** Map vulnerable primitives to NIST FIPS 203 (ML-KEM), FIPS 204 (ML-DSA), FIPS 205 (SLH-DSA), and hybrid transitional standards.
8. **Export Multi-Format Deliverables:** Produce CBOM JSON, SARIF 2.1.0 (for GitHub / IDE code scanning), Executive HTML Reports, ReportLab A4 PDF reports, CSV inventories, and Markdown summaries.
9. **Dedicated Stitch Cyber-Workstation:** 100% Streamlit-free user interface built with React, TypeScript, Vite, Tailwind CSS, and Stitch-designed cybersecurity workstation aesthetics.

---

## 🏛️ 2. Architecture & Pipeline

```text
┌────────────────────────────────────────────────────────────────────────┐
│               REACT + TYPESCRIPT + VITE STITCH WORKSTATION             │
│                       (Port 5173 / Localhost)                         │
│                                                                        │
│   • Dashboard             • Finding Inspector      • CBOM Inspector    │
│   • New Scan Pipeline     • Mosca Simulator        • Terminal & Log    │
│   • Crypto Inventory      • Risk Analysis          • Settings / Policy │
│   • Migration Guidance    • Reports & Evidence                         │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    │ HTTP / REST APIs (JSON)
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                   FASTAPI ASYNC BACKEND ENGINE                         │
│                       (Port 8000 / Localhost)                         │
│                                                                        │
│   GET  /api/dashboard          GET  /api/risk      GET  /api/cbom      │
│   POST /api/scans              GET  /api/migration GET  /api/reports   │
│   GET  /api/inventory          GET  /api/findings  GET  /api/terminal  │
│   GET  /api/mosca              POST /api/mosca     GET  /api/settings  │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                 EXISTING PYTHON ECDAT ANALYSIS CORE                    │
│                                                                        │
│  PROJECT SOURCE ROOT / ARTIFACTS                                       │
│        │                                                               │
│        ├── Source Code (.py, .js, .java, .ts) ──► Python AST Visitor   │
│        ├── Manifests (requirements, pom, etc.) ──► Multi-Ecosystem     │
│        ├── Certificates (.pem, .der, .p12, .pub) ─► X.509 + Keystores  │
│        ├── Server Configs (nginx, openssl, etc.) ─► TLS Protocols      │
│        └── Java Bytecode (.class, .jar) ─────────► Offline Constant    │
│                                 │                                      │
│                                 ▼                                      │
│                 RAW FORENSIC EVIDENCE & NORMALIZATION                  │
│                 (File, Line, Rule ID, Snippet, Provenance)             │
│                                 │                                      │
│                                 ▼                                      │
│                 CROSS-SCANNER DEDUPLICATION                            │
│                 (Confidence upgrade & normalized usage)                │
│                                 │                                      │
│                                 ▼                                      │
│                 POST-QUANTUM CLASSIFICATION & HNDL/TNFL                │
│                 (Shor-Broken, Grover-Weakened, Legacy, Safe)           │
│                                 │                                      │
│                                 ▼                                      │
│                 MOSCA LIFETIME MODEL (X + Y > Z)                       │
│                                 │                                      │
│                                 ▼                                      │
│                 EXPLAINABLE RISK ENGINE (NTRO FORMULA)                 │
│                                 │                                      │
│                                 ▼                                      │
│                 PQC RECOMMENDATIONS (NIST FIPS 203/204)                │
│                                 │                                      │
│                                 ▼                                      │
│                 CYCLONEDX 1.6 CBOM SERIALIZATION & VALIDATION          │
│                                 │                                      │
│                                 ▼                                      │
│     MULTI-FORMAT DELIVERABLES (CBOM, SARIF, HTML, PDF, CSV, Logs)      │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 🖥️ 3. All 11 Stitch Screens

The user interface completely replaces Streamlit with 11 custom-crafted workstation screens matching Stitch design specifications (`Project ID: 15951502437945520827`):

| # | Route | Screen Title | Key Capabilities |
|---|---|---|---|
| **1** | `/dashboard` | **Cryptographic Security Overview** | Hero KPI metrics, risk breakdown, quantum exposure distribution, recent findings list, quick scan CTA. |
| **2** | `/scan/new` | **New Scan Configuration** | Target path selection, multi-scanner checklist (Python AST, Java, Manifests, Certs, Configs), real-time 8-stage execution pipeline. |
| **3** | `/inventory` | **Crypto Inventory** | Searchable cryptographic asset table, multi-parameter filters (Algorithm, Quantum Status, Threat, Risk Band), pagination. |
| **4** | `/findings/:id` | **Finding Inspector** | Dual-column workbench: Asset Parameters, Shor/Grover impact, Mosca theorem check, Quantitative risk card, and IDE code viewer with syntax highlighting and highlighted vulnerable lines. |
| **5** | `/mosca` | **Mosca Simulator** | Interactive sliders for Data Lifetime ($X$), Migration Duration ($Y$), and CRQC Horizon ($Z$), presets (2030, 2035, 2040), real-time equation solving ($X + Y > Z$), HNDL verdict, and visual exposure timeline (2026–2040). |
| **6** | `/risk` | **Cryptographic Risk Analysis** | Global threat exposure gauge, full RFC-NTRO-892 mathematical formula breakdown, 5 weighted factor cards, top risk-ranked findings table. |
| **7** | `/migration` | **Post-Quantum Migration Guidance** | Bento metric cards, 3-stage architectural pipeline (Classical Vulnerable $\to$ Dual-Key Hybrid $\to$ Pure Post-Quantum Lattice), deterministic NIST FIPS 203/204 transition rules. |
| **8** | `/cbom` | **CycloneDX 1.6 CBOM** | Real-time CycloneDX 1.6 schema verification banner, discovered components tree, live syntax-highlighted raw CBOM JSON viewer, export actions. |
| **9** | `/terminal` | **Terminal & Scan Log** | Live daemon telemetry stream, execution ID, log level filtering (ALL, INFO, SUCCESS, WARNING, CRITICAL), auto-scroll, regex filter, copy buffer, raw log export. |
| **10** | `/settings` | **Settings & Security Policies** | 7 configuration domains: AST parsers, quantum classification defaults, risk weights, CBOM schema strictness, air-gapped security guardrails. |
| **11** | `/reports` | **Reports & Evidence Deliverables** | 6 verified audit deliverables (Executive HTML, Technical Dossier, CSV Matrix, CBOM JSON, System Logs, Migration Plan), in-app live preview modal, verified download actions. |

---

## ⚙️ 4. Installation & Setup

### Prerequisites
- Python 3.10+ (Tested on Python 3.11, 3.12, and 3.14)
- Node.js 18+ & npm
- Git

### Quick Setup (Local Environment)
```bash
# Clone the repository
git clone https://github.com/shaikmohammedyasin-create/ECDAT-SIH2026.git
cd ECDAT-SIH2026

# Create and activate Python virtual environment
python -m venv venv
# On Windows PowerShell:
.\venv\Scripts\Activate.ps1
# On Linux/macOS:
source venv/bin/activate

# Install backend dependencies
pip install -r requirements.txt

# Install frontend dependencies
cd frontend
npm install
cd ..
```

---

## 🚀 5. Running ECDAT

### Option A: Single-Command Unified Launcher (Recommended)
```bash
python run.py
```
This automatically starts:
- **FastAPI Backend:** `http://127.0.0.1:8000` (Docs: `http://127.0.0.1:8000/docs`)
- **React Frontend:** `http://localhost:5173`
- Automatically opens your default web browser to the ECDAT Security Workstation!

### Option B: Independent Service Startup
**Terminal 1 (Backend API):**
```bash
python run.py --backend-only
# Or directly via uvicorn:
uvicorn backend.api.main:app --host 127.0.0.1 --port 8000 --reload
```

**Terminal 2 (React Frontend):**
```bash
cd frontend
npm run dev
```

---

## 📊 6. Supported Inputs & Manifests

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

## 📑 7. Reports & Deliverables

Every scan produces 6 standard deliverables in `output/`:

1. **`cbom.json`**: CycloneDX 1.6 Cryptographic BOM strictly validated against `schemas/bom-1.6.schema.json`.
2. **`inventory.csv`**: Tabular asset inventory with rule IDs, locations, quantum status, and risk bands.
3. **`findings.sarif`**: Schema-valid SARIF 2.1.0 output for automated CI/CD code scanning.
4. **`report.html`**: Standalone, dark-palette executive security report with interactive metrics.
5. **`report.pdf`**: Printable executive risk report built via ReportLab.
6. **`summary.md`**: Executive markdown summary suitable for commit comments and release notes.

---

## 🧪 8. Automated Testing & Verification

Run the full automated test suite:
```bash
.\venv\Scripts\python.exe -m pytest tests/ -v
```

### Verified Test Results:
- **59 passed, 0 failed** across all test suites:
  - **48 Core Cryptographic Tests:** AST detection, X.509 parsing, constant pool reading, quantum classification, HNDL/TNFL, Mosca inequality, risk scoring, PQC recommendations, CycloneDX 1.6 serialization & schema validation.
  - **11 FastAPI Endpoint Tests:** Dashboard, New Scan, Inventory, Finding Inspector, Mosca Simulator, Risk Analysis, Migration Guidance, CBOM, Reports, Terminal, and Settings.
- **Frontend Build Verification:**
  - `cd frontend && npm run build` completes with **0 TypeScript errors**.

---

## 🔒 9. Security Controls & Air-Gap Guarantee

- **100% Air-Gapped Operation:** Zero external network calls, tracking beacons, or telemetry.
- **Zero Private Key Persistence:** Scanners inspect algorithms and parameters only; never persist or log private keys.
- **Path Traversal Protection:** Target scan paths are sandboxed and validated against directory escape attacks.
- **Zip Slip & Archive Bomb Guard:** JAR and archive readers cap entry extraction and enforce safe path canonicalization.
- **XML Entity Defense:** Uses `defusedxml` to block XML external entity (XXE) and billion-laughs attacks.

---

## 🎬 10. Reproducible Demonstration Workflow

To demonstrate ECDAT for evaluators in 60 seconds:
1. Run `python run.py` (opens React Workstation at `http://localhost:5173`).
2. Show the **Dashboard**: observe Shor-broken assets, HNDL confidentiality risks, and Mosca violations.
3. Go to **New Scan** (`/scan/new`): select `test_corpus` and click **Initiate AST Cryptographic Scan** to watch the real-time pipeline execute.
4. Go to **Crypto Inventory** (`/inventory`): filter by algorithm or risk band, and click **Inspect** on any finding (e.g. `RSA-2048`).
5. In **Finding Inspector** (`/findings/1`): examine the AST parameters, Shor/Grover impact, and IDE source code viewer with highlighted vulnerable lines.
6. Go to **Mosca Simulator** (`/mosca`): drag the slider from 2035 to 2030 to demonstrate live re-calculation of the theorem deficit window ($X + Y > Z$).
7. Go to **Risk Analysis** (`/risk`): show the explainable 5-factor deterministic formulation.
8. Go to **Migration Guidance** (`/migration`): review the 3-stage hybrid and NIST lattice roadmap.
9. Go to **CycloneDX 1.6 CBOM** (`/cbom`): demonstrate **CBOM Schema Status: VALID ✓ (0 Errors)** and inspect the raw JSON.
10. Go to **Terminal / Log** (`/terminal`): observe live stream telemetry and filter by log level.
11. Go to **Reports & Evidence** (`/reports`): preview executive reports in-app and download deliverables.


## License

ECDAT is licensed under the [MIT License](LICENSE).
