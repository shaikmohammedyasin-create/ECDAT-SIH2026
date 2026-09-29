# ECDAT — SIH 2026 Implementation Source of Truth
## Enterprise Cryptographic Discovery & Analysis Tool
### PS ID 26164 · NTRO · Software · Blockchain & Cybersecurity

**Version:** 1.0 — MVP implementation contract  
**Date:** 29 Sep 2026  
**Purpose:** This file is the implementation-ready source of truth for the ECDAT prototype, the final 6-slide SIH deck, the demo, and the team's division of work.

> **Important:** The architecture and long-term vision from the team's technical blueprint are retained, but this file explicitly separates what must work for the SIH prototype from what is roadmap-only. Do not expand the MVP scope unless the core acceptance gates are already passing.

---

# 1. Executive Pitch

> **ECDAT is an air-gap-ready platform that discovers cryptographic assets across source code, dependencies, certificates, binaries, containers, configurations and authorised live endpoints; normalises them into a CycloneDX 1.6 CBOM; evaluates quantum risk using Mosca's X + Y > Z framework; and recommends PQC or hybrid migration actions.**

The core workflow is:

```text
INPUT
  ↓
DISCOVER
  ↓
NORMALISE
  ↓
CLASSIFY
  ↓
QUANTUM RISK + MOSCA
  ↓
RECOMMEND PQC / HYBRID
  ↓
CYCLONEDX 1.6 CBOM
  ↓
DASHBOARD / REPORT
```

The prototype must demonstrate this complete vertical slice before optional features are added.

---

# 2. Problem Statement Coverage

ECDAT must address the following PS requirements.

| PS requirement | ECDAT response | MVP status |
|---|---|---|
| Catalogue algorithms | Source/config/dependency detectors | **Must work** |
| Catalogue keys | PEM/DER/key metadata detection | **Must work** |
| Catalogue certificates | X.509 parsing | **Must work** |
| Catalogue protocols | TLS/config detection | **Must work** |
| Catalogue libraries | Dependency/version detection | **Must work** |
| Catalogue hardware modules | PKCS#11/HSM/config detection | Prototype metadata; deeper live HSM = roadmap |
| Catalogue cloud services | IaC/KMS configuration detection | Roadmap for live cloud APIs |
| Internal systems | Source/dependency/local artefact scanning | **Must work** |
| External systems | Authorised TLS endpoint probe | **Must work if time permits; otherwise clearly marked extension** |
| Quantum risk | Shor/Grover classification | **Must work** |
| Sensitive-data risk | HNDL/TNFL + data lifetime | **Must work** |
| Classification | Type/lifetime/business criticality | **Must work** |
| Mosca | X + Y > Z per asset | **Must work** |
| PQC/hybrid recommendation | Deterministic recommendation table | **Must work** |
| Standardised output | CycloneDX 1.6 CBOM | **Must work** |
| Interactive GUI | Streamlit prototype | **Must work** |
| Binary scanning | Library/version/symbol detection | Minimal prototype / roadmap |
| Container scanning | Basic image/layer extraction | Minimal prototype / roadmap |

---

# 3. NON-NEGOTIABLE MVP CONTRACT

## 3.1 Must be working

The following are the acceptance gates for the prototype:

1. Scan a local project/repository.
2. Detect known cryptographic usage in **Python and Java**.
3. Detect at least the following classes:
   - RSA
   - ECDH/ECDSA/EC
   - AES
   - SHA-256/SHA-384/SHA-512
   - MD5/SHA-1
   - weak/legacy algorithms where planted
4. Capture evidence:
   - file
   - line where available
   - detector/rule
   - detected algorithm
   - parameters/key size/mode where available
   - confidence
5. Parse at least:
   - `requirements.txt`
   - `pom.xml`
6. Detect crypto libraries and versions from dependency manifests.
7. Parse PEM/DER X.509 certificates.
8. Classify every finding by:
   - asset type
   - function/primitive
   - quantum status
   - lifetime
   - business criticality
   - exposure
9. Apply HNDL/TNFL where applicable.
10. Run Mosca's inequality:
    - `X` = required security/data/trust lifetime
    - `Y` = migration time
    - `Z` = scenario CRQC horizon
    - at risk when `X + Y > Z`
11. Produce a transparent 0–100 priority/risk score.
12. Produce a deterministic PQC/hybrid recommendation.
13. Generate a **CycloneDX 1.6 CBOM JSON**.
14. Validate the CBOM against the appropriate CycloneDX 1.6 JSON schema.
15. Show results in a working Streamlit dashboard.
16. Run at least one real scan against a controlled corpus.
17. Run at least one scan against a real/open-source target if time and network access permit.
18. Produce screenshots from actual prototype output.
19. Record actual measured counts/times for the final PPT.

## 3.2 Optional only after the above works

- JavaScript/TypeScript source scanning
- TLS endpoint probe
- SSH probe
- dependency graph visualisation
- Docker/OCI layer extraction
- binary library/version analysis
- PDF export
- CSV export
- SARIF export
- local PQC micro-benchmarking
- GitHub Action/CI integration

## 3.3 Roadmap — do not allow these to block the MVP

- Full C/C++/Go/Rust/C#/PHP/Kotlin AST coverage
- Full binary reverse engineering/disassembly
- angr symbolic recovery
- runtime hooks
- live HSM mechanism enumeration
- live AWS/Azure/GCP inventory
- automatic pull requests
- enterprise RBAC/Keycloak
- PostgreSQL/Neo4j migration
- distributed Celery/RQ workers
- full React frontend
- continuous organisation-wide scanning

**Rule:** A roadmap feature may appear in the architecture diagram only if it is clearly labelled **ROADMAP / PLANNED** when it is not implemented.

---

# 4. Scope Decision: Prototype vs Long-Term Platform

The technical blueprint describes a production-scale architecture. The SIH prototype intentionally uses a smaller stack so the vertical slice can be demonstrated reliably.

## 4.1 MVP stack

| Layer | MVP choice |
|---|---|
| Language | Python 3.11+ |
| Source parsing | tree-sitter where useful; regex/AST fallback |
| Python detection | Python AST + crypto API rules |
| Java detection | tree-sitter/regex/API rules |
| Certificates | Python `cryptography` |
| Dependencies | XML/JSON/text parsers |
| Data | SQLite / JSON |
| CBOM | CycloneDX 1.6 JSON |
| Schema validation | `jsonschema` |
| GUI | Streamlit |
| Charts | Plotly |
| Graph | NetworkX/pyvis if implemented |
| PDF | ReportLab or WeasyPrint if implemented |
| TLS | Python `ssl` / sslyze if implemented |
| Container | Docker/OCI extraction if implemented |
| Binary | LIEF/pyelftools if implemented |

## 4.2 Production architecture

The scalable architecture can later use:

```text
React Dashboard
      ↓
REST/API Layer
      ↓
Job Queue / Orchestrator
      ↓
Parallel Discovery Workers
      ↓
Normalisation + Dependency Graph
      ↓
Risk / Mosca / Recommendation Engines
      ↓
CBOM + Reports
```

The production architecture is **vision**, not a requirement to rebuild the MVP.

---

# 5. Design Principles

1. **CBOM-first** — every crypto finding should become a structured asset.
2. **Evidence-based** — findings must show where and how they were detected.
3. **Explainable** — no opaque AI score is required.
4. **Air-gapped ready** — core analysis works without sending source code externally.
5. **Crypto-agility aware** — distinguish configurable crypto from hard-coded crypto.
6. **Deterministic recommendations** — recommendation rules must be inspectable.
7. **Confidence-aware** — static detection is not perfect; report confidence.
8. **Extensible** — scanners can be added without changing the asset model.
9. **Honest reporting** — never invent detection counts, benchmarks, scan times or accuracy.
10. **Security by design** — never persist private key material.

---

# 6. Architecture

```text
┌───────────────────────────────────────────────────────────────┐
│                         INPUTS                                │
│ Repo / ZIP / Dependencies / Certificates / Binary / Image    │
│ Config / IaC / Authorised TLS Endpoint                       │
└──────────────────────────────┬────────────────────────────────┘
                               ↓
┌───────────────────────────────────────────────────────────────┐
│                     DISCOVERY LAYER                           │
│ Source Scanner │ Dependency │ Cert/Key │ Config │ TLS        │
│ Binary Scanner │ Container Scanner (optional MVP)            │
└──────────────────────────────┬────────────────────────────────┘
                               ↓
┌───────────────────────────────────────────────────────────────┐
│                 NORMALISATION / FUSION                        │
│ Unified CryptoAsset schema · deduplication · evidence         │
│ confidence · dependency relationships                          │
└──────────────────────────────┬────────────────────────────────┘
                               ↓
┌───────────────────────────────────────────────────────────────┐
│                   ANALYSIS ENGINE                             │
│ Quantum classification · HNDL/TNFL · lifetime · criticality   │
│ Mosca X + Y > Z · risk score · crypto-agility                │
└──────────────────────────────┬────────────────────────────────┘
                               ↓
┌───────────────────────────────────────────────────────────────┐
│                 RECOMMENDATION ENGINE                         │
│ PQC / Hybrid mapping · security · size · latency · effort     │
└──────────────────────────────┬────────────────────────────────┘
                               ↓
┌───────────────────────────────────────────────────────────────┐
│                         OUTPUTS                               │
│ CycloneDX 1.6 CBOM · Dashboard · CSV · PDF · SARIF           │
└───────────────────────────────────────────────────────────────┘
```

---

# 7. Discovery Engines

## 7.1 Source-code scanner — MVP

### Languages

**Required:**
- Python
- Java

**Optional:**
- JavaScript/TypeScript

**Roadmap:**
- C/C++
- Go
- Rust
- C#
- PHP
- Kotlin

### Detection examples

Python:

```python
RSA.generate(2048)
AES.new(key, AES.MODE_ECB)
hashlib.md5(data)
hashlib.sha256(data)
ec.generate_private_key(...)
```

Java:

```java
KeyPairGenerator.getInstance("RSA")
kpg.initialize(2048)
Cipher.getInstance("AES/ECB/PKCS5Padding")
MessageDigest.getInstance("SHA-1")
Signature.getInstance("SHA256withECDSA")
```

### Capture

Every finding should attempt to capture:

```text
asset
primitive
algorithm
parameter_set
key_size
mode
padding
curve
file
line
evidence
rule_id
confidence
```

### Confidence

Suggested interpretation:

| Confidence | Meaning |
|---|---|
| High | Resolved API call / structured parser |
| Medium | Strong string or configuration evidence |
| Low | Heuristic/constant signature |

---

# 8. Dependency Scanner

Required MVP inputs:

```text
requirements.txt
pom.xml
```

Optional:

```text
package.json
go.mod
Cargo.toml
build.gradle
```

Detect:

- package name
- version
- crypto relevance
- known PQC support if the local KB contains verified information
- EOL/weak-version information only when backed by a verified KB entry

Example relationships:

```text
Application
   ↓ uses
Python cryptography
   ↓ implements
RSA / AES / ECDSA
```

---

# 9. Certificate & Key Scanner

Support:

- PEM
- DER
- X.509
- PKCS#12/JKS where practical
- SSH public keys where practical

Extract metadata:

- subject
- issuer
- SAN
- signature algorithm
- public-key algorithm
- key size/curve
- validity start/end
- key usage
- self-signed status
- chain information

### Security rule

**Never store private key material.**

Store only metadata, evidence and a non-reversible fingerprint/hash when needed.

---

# 10. Configuration / IaC Scanner

MVP examples:

```text
nginx.conf
sshd_config
openssl.cnf
Java security configuration
Kubernetes YAML
Terraform
```

Detect:

- TLS versions
- cipher suites
- key-exchange settings
- certificate references
- RSA/ECC key specifications
- PKCS#11 references
- KMS/HSM configuration indicators

Live cloud APIs are roadmap unless already implemented.

---

# 11. Live Endpoint Scanner

If implemented for MVP:

- only scan explicitly authorised targets
- require an allow-list/authorisation confirmation
- inspect TLS versions
- inspect cipher suites
- inspect certificate chain
- inspect key-exchange group
- flag whether a hybrid PQC group such as `X25519MLKEM768` is negotiated
- inspect SSH KEX when supported

Do not scan arbitrary third-party systems without authorisation.

---

# 12. Binary & Container Scanning

## Binary — MVP-lite

If time permits, detect:

- ELF/PE/JAR
- linked crypto libraries
- library version strings
- imported symbols such as OpenSSL crypto APIs

Use confidence labels.

**Known limitation:** stripped/obfuscated binaries reduce static detection confidence.

## Container — MVP-lite

If time permits:

1. accept a Docker/OCI image or `docker save` archive
2. inspect filesystem/package metadata
3. search for certificates/keys/configs
4. identify crypto libraries
5. record the image/layer where practical

Full container intelligence is roadmap if it threatens the core MVP deadline.

---

# 13. Unified CryptoAsset Schema

Each finding becomes a normalised asset.

```json
{
  "asset_id": "ca-001",
  "asset_type": "algorithm",
  "primitive": "pke",
  "name": "RSA",
  "parameter_set": "2048",
  "mode": null,
  "padding": "OAEP",
  "curve": null,
  "classical_security_bits": 112,
  "quantum_vuln_class": "SHOR_BROKEN",
  "nist_quantum_security_level": 0,
  "location": {
    "kind": "source",
    "path": "src/auth/keys.py",
    "line": 42
  },
  "evidence": {
    "rule_id": "PY-RSA-001",
    "confidence": 0.95
  },
  "component_ref": "pkg:pypi/cryptography@version",
  "application": "demo-app",
  "environment": "local",
  "exposure": "internal",
  "data_sensitivity": "confidential",
  "data_lifetime_years": 15,
  "business_criticality": 4,
  "migration_time_years": 3
}
```

---

# 14. Quantum Vulnerability Classification

| Class | Meaning | Examples |
|---|---|---|
| `SHOR_BROKEN` | Public-key systems vulnerable to Shor | RSA, DH, DSA, ECDH, ECDSA, EdDSA, X25519 |
| `GROVER_WEAKENED` | Reduced theoretical security margin | AES-128 / short symmetric keys |
| `QUANTUM_SAFE` | Considered resistant for this analysis | AES-256, SHA-384/512, SHA-3, ML-KEM, ML-DSA, SLH-DSA |
| `CLASSICALLY_BROKEN` | Already broken independent of quantum | MD5, SHA-1, DES, 3DES, RC4, RSA < 2048 |

### Important interpretation

The prototype must **not** treat AES-128 as equivalent to RSA/ECC quantum exposure. It is an advisory priority in this model.

---

# 15. HNDL and TNFL

## HNDL — Harvest Now, Decrypt Later

Relevant primarily to:

- RSA key exchange/encryption
- DH/ECDH/X25519 key exchange
- long-lived encrypted data

## TNFL — Trust Now, Forge Later

Relevant primarily to:

- code signing
- firmware signing
- root CAs
- certificates
- long-lived signatures
- legal/trust artefacts
- other persistent authenticity requirements

The dashboard should display these labels where applicable.

---

# 16. Classification

Every asset should have:

### Type

```text
Algorithm
Key
Certificate
Protocol
Library
Hardware Module
Cloud Service
```

### Function

```text
Key exchange / KEM
Encryption
Signature
Hash
MAC
KDF
Symmetric encryption
```

### Lifetime

Use editable organisation defaults.

Example:

```text
Short      < 5 years
Medium     5–15 years
Long       15–25 years
Archival   > 25 years
```

### Business criticality

```text
1 = Low
2 = Moderate
3 = High
4 = Mission-critical
5 = National-security / critical infrastructure
```

### Exposure

```text
External-facing
Internal
Offline / air-gapped
```

---

# 17. Mosca Risk Engine

## Formula

```text
X = time data/trust must remain secure
Y = time required to migrate
Z = time until the selected CRQC scenario

At risk when:

X + Y > Z
```

The implementation should calculate:

```text
margin = Z - (X + Y)

at_risk = margin < 0
```

Optional urgency:

```text
urgency = clamp(-(margin) / (X + Y), 0, 1)
```

## Scenario configuration

Use **scenario years**, not hard-coded assumptions about when a CRQC will actually exist.

Recommended default scenario years for the prototype:

| Scenario | Default CRQC year | Meaning |
|---|---:|---|
| Aggressive | 2030 | Early/tail-risk planning case |
| Baseline | 2035 | Mid-2030s planning case |
| Conservative | 2040 | Slower-progress planning case |

The tool must compute:

```text
Z = scenario_year - current_year
```

The UI must state:

> **These are planning scenarios, not predictions of a CRQC arrival date.**

Users should be able to change the scenario year.

---

# 18. Mosca Example

Example:

```text
Current year = 2026
Scenario year = 2035
Z = 9 years

X = 25 years
Y = 5 years

X + Y = 30
30 > 9

Result: At risk
```

For authenticity:

```text
X = period during which the signature/trust must remain valid
```

Do not apply the same confidentiality interpretation to signatures/certificates.

---

# 19. Risk / Priority Score

Use a transparent heuristic:

```text
Priority = 100 × (
    0.35 × QuantumExposure
  + 0.25 × BusinessCriticality
  + 0.15 × ExposureSurface
  + 0.15 × DataSensitivity
  + 0.10 × (1 - CryptoAgility)
)
```

Inputs must be normalised to `[0,1]`.

### Interpretation

- QuantumExposure: derived from vulnerability class and Mosca gap
- BusinessCriticality: 1–5 mapped to `[0,1]`
- ExposureSurface: external > internal > offline
- DataSensitivity: public < internal < confidential < secret
- CryptoAgility: configurable/provider-based > hard-coded/static/embedded

**Important:** these are heuristic defaults, not scientific constants. Show them transparently and make them configurable.

Suggested bands:

```text
80–100  Critical
60–79   High
40–59   Medium
20–39   Low
<20     Info
```

Classically broken crypto may receive a separate `Hygiene-Critical` label.

---

# 20. PQC / Hybrid Recommendation Engine

The MVP can use deterministic rules rather than a complex optimiser.

| Detected asset | Primary recommendation | Alternative |
|---|---|---|
| RSA/ECDH/X25519 key exchange | Hybrid X25519 + ML-KEM-768 | ML-KEM-768 |
| RSA encryption/key wrapping | ML-KEM-768 + AES-256 envelope encryption | — |
| RSA/ECDSA application signatures | ML-DSA-65 | ML-DSA-44 |
| Firmware/code signing | LMS/XMSS or ML-DSA | SLH-DSA |
| Long-lived root trust | SLH-DSA / ML-DSA high-assurance profile | Hybrid transition |
| AES-128 for long-lived data | AES-256 | — |
| MD5/SHA-1 | SHA-384/SHA-512/SHA-3 | — |
| DES/3DES/RC4 | AES-256-GCM or ChaCha20 | — |

The recommendation output should contain:

```text
Detected algorithm
Why it is risky
Recommended algorithm
Hybrid option
Migration effort
Size impact if known
Latency impact if measured
Standard/reference
```

Do not quote benchmark latency unless measured locally.

---

# 21. CBOM Output

## Primary format

**CycloneDX 1.6 JSON**

Each crypto asset should be represented as a `cryptographic-asset` with the relevant `cryptoProperties`.

Include where supported:

- asset type
- primitive
- parameter set
- curve
- mode
- padding
- crypto functions
- classical security level
- quantum security level
- certificate properties
- protocol properties
- OID
- evidence occurrences
- relationships/dependencies

ECDAT-specific metadata can use namespaced properties such as:

```text
ecdat:threat
ecdat:mosca-margin-years
ecdat:risk-score
ecdat:recommendation
ecdat:confidence
```

## Example

```json
{
  "bomFormat": "CycloneDX",
  "specVersion": "1.6",
  "components": [
    {
      "type": "cryptographic-asset",
      "name": "RSA-2048",
      "bom-ref": "crypto/algo/rsa-2048",
      "cryptoProperties": {
        "assetType": "algorithm",
        "algorithmProperties": {
          "primitive": "pke",
          "parameterSetIdentifier": "2048",
          "cryptoFunctions": ["encrypt", "decrypt"],
          "classicalSecurityLevel": 112,
          "nistQuantumSecurityLevel": 0
        }
      },
      "evidence": {
        "occurrences": [
          {
            "location": "src/auth/keys.py",
            "line": 42
          }
        ]
      },
      "properties": [
        {
          "name": "ecdat:threat",
          "value": "HNDL"
        },
        {
          "name": "ecdat:risk-score",
          "value": "91"
        },
        {
          "name": "ecdat:recommendation",
          "value": "ML-KEM-768 hybrid transition"
        }
      ]
    }
  ]
}
```

### Validation gate

Do not claim “CycloneDX compliant” unless the generated JSON has actually been validated against the intended CycloneDX 1.6 schema.

---

# 22. GUI — Streamlit MVP

## Page 1 — Dashboard

Show:

- total assets
- quantum-vulnerable assets
- classically broken assets
- high/critical count
- quantum-readiness indicator
- risk distribution
- top priorities
- scenario selector

## Page 2 — New Scan

Inputs:

```text
Local folder / ZIP
Dependency files
Certificate folder
Optional binary/image
Optional authorised endpoint
```

Show scan progress and completion status.

## Page 3 — Inventory

Columns:

```text
Type
Algorithm
Parameter
Version
Location
Quantum class
HNDL/TNFL
Criticality
Exposure
Mosca margin
Risk
Recommendation
```

## Page 4 — Asset Detail

Show:

```text
Detected asset
Evidence
Rule
Confidence
Threat
X
Y
Z
X + Y
Mosca margin
Risk score
Recommendation
Migration effort
```

## Page 5 — Mosca Simulator

Controls:

```text
Scenario year
X
Y
```

Output:

```text
X + Y
Z
Margin
At-risk status
```

## Page 6 — Reports

Buttons where implemented:

```text
Download CBOM JSON
Download CSV
Download PDF
Download SARIF
```

---

# 23. Controlled Validation Corpus

## No large external dataset is required for the MVP.

The prototype needs a **small controlled ground-truth corpus** plus one or more real/open-source targets.

Recommended project structure:

```text
test_corpus/
├── python/
│   ├── crypto_sample.py
│   └── weak_crypto_sample.py
├── java/
│   ├── CryptoSample.java
│   └── WeakCryptoSample.java
├── dependencies/
│   ├── requirements.txt
│   └── pom.xml
├── certificates/
│   └── test_cert.pem
├── configs/
│   ├── nginx.conf
│   └── sshd_config
└── expected_findings.json
```

The controlled corpus should contain planted examples with known expected findings.

This is **validation data**, not a claim that the project requires a large ML dataset.

---

# 24. Suggested Real Validation Targets

If time/network access allows:

1. OpenSSL source or build
2. Older OpenSSL 1.1.1 build/container
3. Bouncy Castle Java source/JAR
4. pyca/cryptography or small Flask/Django project
5. nginx/Apache container
6. intentionally weak demo application
7. local authorised TLS endpoint

Do not let downloading or configuring external targets block the controlled-corpus demo.

---

# 25. Metrics

Only report numbers actually measured.

Minimum useful metrics:

```text
Total assets detected
Quantum-vulnerable assets
Classically broken assets
Scan time
CBOM validation status
Number of planted findings detected
False positives
```

Optional:

```text
Precision
Recall
F1
Binary detection accuracy
Container-layer attribution accuracy
```

Example format:

```text
Controlled corpus:
12 planted crypto assets
11 detected
1 missed
2 false positives

Precision = measured value
Recall    = measured value
F1        = measured value
```

Never copy an example number into the PPT as if it were a real result.

---

# 26. Security Rules

1. Never upload source code to an external service for core analysis.
2. Never persist private key material.
3. Hash/fingerprint sensitive artefacts only when needed.
4. Restrict live endpoint scans to authorised targets.
5. Keep audit logs for live scans.
6. Treat uploaded repositories as untrusted input.
7. Use sandboxing where feasible.
8. Do not execute arbitrary repository code merely to analyse it.
9. Sanitise file paths and archive extraction.
10. Do not expose secrets in dashboard screenshots.

---

# 27. Repository Structure

Recommended:

```text
ecdat/
├── app.py
├── README.md
├── requirements.txt
├── config/
│   └── defaults.yaml
├── ecdat/
│   ├── models/
│   │   └── crypto_asset.py
│   ├── scanners/
│   │   ├── python_scanner.py
│   │   ├── java_scanner.py
│   │   ├── dependency_scanner.py
│   │   ├── certificate_scanner.py
│   │   ├── config_scanner.py
│   │   ├── tls_scanner.py
│   │   ├── binary_scanner.py
│   │   └── container_scanner.py
│   ├── analysis/
│   │   ├── classifier.py
│   │   ├── quantum_rules.py
│   │   ├── mosca.py
│   │   └── risk.py
│   ├── recommendations/
│   │   └── engine.py
│   ├── cbom/
│   │   ├── builder.py
│   │   └── validator.py
│   ├── reports/
│   │   ├── csv_report.py
│   │   └── pdf_report.py
│   └── knowledge/
│       ├── algorithms.yaml
│       ├── recommendations.yaml
│       └── libraries.yaml
├── test_corpus/
├── tests/
├── outputs/
└── docs/
    └── ECDAT_SIH2026_IMPLEMENTATION_SOURCE_OF_TRUTH.md
```

The exact folder structure can differ if the current implementation already has an equivalent modular design. Do not refactor working code solely to match this tree.

---

# 28. Minimum API / Internal Interfaces

## Scanner output

Every scanner should return a common finding structure:

```python
{
    "asset_type": "...",
    "primitive": "...",
    "name": "...",
    "parameter_set": "...",
    "location": {...},
    "evidence": {...},
    "confidence": 0.0,
    "source": "python_scanner"
}
```

## Normaliser

```text
raw findings
    ↓
normalised CryptoAsset objects
    ↓
deduplicated assets
```

## Risk engine

```text
CryptoAsset
    ↓
quantum classification
    ↓
HNDL/TNFL
    ↓
X/Y/Z
    ↓
Mosca result
    ↓
risk/priority
```

## Recommendation engine

```text
CryptoAsset + risk context
    ↓
recommendation rules
    ↓
primary + alternatives
    ↓
migration rationale
```

---

# 29. Knowledge Base

Keep algorithm and recommendation data outside hard-coded business logic where practical.

Minimum fields:

```yaml
algorithm: RSA
family: public-key
quantum_class: SHOR_BROKEN
hndl: true
tnfl: true
minimum_parameter: 2048
recommendation:
  primary: ML-KEM-768
  transition: X25519MLKEM768
```

Do not include uncertain standards or library-version claims without verifying them before the final PPT.

---

# 30. Recommended Standards / References

Use these as technical references where applicable:

- NIST FIPS 203 — ML-KEM
- NIST FIPS 204 — ML-DSA
- NIST FIPS 205 — SLH-DSA
- NIST SP 800-208 — LMS/XMSS
- NIST IR 8547 — migration/deprecation planning draft; do not describe a draft as a mandate
- NIST SP 1800-38B — cryptographic discovery/migration guidance
- CycloneDX 1.6 — CBOM
- Mosca's quantum-risk framework
- CNSA 2.0
- relevant India PQC / SBOM / CBOM guidance after primary-source verification

### Verification rule

Any number, date, standard status, deployment claim, benchmark, or policy claim placed on the final slide must be re-verified against its primary source before submission.

---

# 31. Six-Slide SIH Mapping

The final submission is **6 slides maximum including the title slide**.

## Slide 1 — Title

```text
Problem Statement ID: 26164
Enterprise Cryptographic Discovery & Analysis Tool (ECDAT)
NTRO
Blockchain & Cybersecurity
Software
Team ID / Team Name
```

## Slide 2 — Idea Title

Core message:

```text
Discover → Quantify → Migrate
```

Show:

- unified discovery
- CycloneDX 1.6 CBOM
- Mosca X + Y > Z
- HNDL/TNFL
- PQC/hybrid recommendation
- air-gapped operation

## Slide 3 — Technical Approach

Show:

```text
Inputs
→ Discovery
→ Normalisation
→ Risk/Mosca
→ Recommendation
→ CBOM/Dashboard
```

Include one or two **real prototype screenshots**.

## Slide 4 — Feasibility and Viability

Show:

- working prototype evidence
- open-source stack
- air-gapped deployment
- measured scan metrics
- challenges → mitigations
- MVP vs roadmap boundary

## Slide 5 — Impact and Benefits

Show:

- cryptographic inventory
- quantum-risk prioritisation
- HNDL/TNFL protection
- migration planning
- CBOM procurement/audit value
- developer remediation
- government/CII applicability

## Slide 6 — Research and References

Use only verified references.

Do not overload the slide with URLs. Use compact source names and QR/link formatting if allowed by the template.

---

# 32. Demo Script

The demo should tell one continuous story.

### Step 1 — Start with a vulnerable project

Scan the controlled Python/Java project.

### Step 2 — Show discovery

Example:

```text
RSA-2048
ECDSA P-256
AES-128
AES-256-GCM
SHA-1
SHA-256
```

Show file/line evidence.

### Step 3 — Show classification

Explain:

```text
RSA/ECDH → Shor-vulnerable
AES-128 → Grover advisory
AES-256/SHA-256 → safe in this model
SHA-1 → classically broken
```

### Step 4 — Show Mosca

Select an asset.

Display:

```text
X = data lifetime
Y = migration time
Z = scenario horizon

X + Y > Z
```

Move the scenario slider.

### Step 5 — Show recommendation

Example:

```text
ECDH/X25519
→ Hybrid X25519 + ML-KEM-768
→ ML-KEM-768 later
```

### Step 6 — Show CBOM

Open the generated CycloneDX 1.6 JSON.

Show schema validation.

### Step 7 — Show dashboard

Finish with:

```text
Top risks
Migration order
Quantum readiness
CBOM export
```

---

# 33. Acceptance Tests

The prototype is ready for the final PPT only when these pass.

| Test | Pass condition |
|---|---|
| Python scan | Known planted Python crypto findings detected |
| Java scan | Known planted Java findings detected |
| Dependency scan | `requirements.txt` and `pom.xml` parsed |
| Certificate scan | Test certificate metadata extracted |
| Normalisation | Findings converted to common asset schema |
| Quantum rules | Known algorithms classified correctly |
| HNDL/TNFL | Applicable findings receive correct threat label |
| Mosca | X/Y/Z calculation recomputes correctly |
| Scenario change | Risk changes when Z changes |
| Risk score | Score is deterministic and explainable |
| Recommendation | Known weak algorithms map to expected alternatives |
| CBOM generation | Valid CycloneDX 1.6 JSON generated |
| CBOM validation | Schema validator passes |
| Dashboard | Scan results visible without manual database edits |
| Evidence | At least file/line or equivalent location shown |
| Security | No private key material persisted |
| Real screenshot | Every PPT screenshot comes from actual prototype |
| Metrics | Every PPT metric has a reproducible measurement |

---

# 34. What Must NOT Happen

Do not:

- invent benchmark numbers
- invent precision/recall
- claim full language coverage when only Python/Java work
- claim full binary analysis when only version strings are detected
- claim live cloud discovery when only IaC is parsed
- call a roadmap feature “implemented”
- describe CRQC dates as predictions
- describe draft NIST guidance as a final mandate
- store private keys
- add a large dataset merely to make the project look like an AI system
- replace the working MVP architecture with a larger stack during the final build
- add React/PostgreSQL/Neo4j/Celery if doing so risks breaking the working prototype

---

# 35. Definition of Done

The project is considered SIH-prototype complete when:

```text
[✓] Controlled corpus scans
[✓] Python + Java crypto discovery
[✓] Evidence captured
[✓] Dependency versions captured
[✓] Certificate metadata captured
[✓] Quantum classification
[✓] HNDL/TNFL
[✓] Type/lifetime/criticality classification
[✓] Mosca X + Y > Z
[✓] Risk score
[✓] PQC/hybrid recommendation
[✓] CycloneDX 1.6 CBOM
[✓] CBOM schema validation
[✓] Streamlit dashboard
[✓] Real screenshots
[✓] Real measured metrics
[✓] 6-slide PDF
```

Everything beyond this is secondary.

---

# 36. Team Working Rule

The project has two documents conceptually:

### This file
**Implementation Source of Truth**

Controls:

- what must be built
- what can be shown
- what is roadmap
- acceptance criteria
- demo
- validation
- PPT claims

### Original Technical Blueprint
**Long-term architecture and technical reference**

Controls:

- scalable architecture
- future scanner coverage
- enterprise deployment concepts
- extended research/reference material

If the two conflict on MVP scope, **this implementation contract wins for the prototype**.

---

# 37. Final Pre-Submission Checklist

## Prototype

- [ ] App launches from a clean environment
- [ ] Controlled corpus scan works
- [ ] Real target scan works where available
- [ ] Dashboard has no placeholder numbers
- [ ] CBOM opens correctly
- [ ] CBOM schema validation passes
- [ ] Mosca calculation manually/programmatically verified
- [ ] Recommendations match the rule table
- [ ] No private keys are included in outputs/screenshots

## Evidence

- [ ] Screenshot of dashboard
- [ ] Screenshot of inventory
- [ ] Screenshot of asset evidence
- [ ] Screenshot of Mosca calculation
- [ ] Screenshot of recommendation
- [ ] Screenshot or excerpt of valid CBOM

## PPT

- [ ] Exactly 6 slides
- [ ] No paragraphs
- [ ] Minimal text
- [ ] Real screenshots only
- [ ] Every number measured
- [ ] Every standards/date claim verified
- [ ] Roadmap items labelled
- [ ] References included
- [ ] Exported to PDF
- [ ] PDF checked after export

---

# 38. One-Line Judge Answer

If a judge asks:

> **“What exactly does ECDAT do?”**

Answer:

> **“ECDAT finds cryptography, proves where it is, quantifies quantum exposure with Mosca, recommends the migration path, and exports the result as a standard CBOM — all without sending sensitive source data outside the environment.”**

---

# 39. Change Control

When adding a feature, classify it first:

```text
MVP
OPTIONAL MVP
ROADMAP
```

A new feature must not delay an incomplete MVP acceptance gate.

Before changing architecture, ask:

1. Does the change improve a required PS capability?
2. Does it improve the actual demo?
3. Can it be tested before submission?
4. Does it risk breaking working code?
5. Can the same result be achieved with the current stack?

If the answer to #4 is yes and #1–#3 are weak, do not make the change.

---

# 40. Final Engineering Principle

> **Build the smallest complete ECDAT, not the largest incomplete ECDAT.**

The winning prototype story is not the number of modules in the repository.

It is the demonstrated chain:

```text
REAL INPUT
   ↓
REAL CRYPTO DISCOVERY
   ↓
REAL EVIDENCE
   ↓
REAL QUANTUM CLASSIFICATION
   ↓
REAL MOSCA CALCULATION
   ↓
REAL RISK PRIORITY
   ↓
REAL PQC / HYBRID RECOMMENDATION
   ↓
VALID CYCLONEDX 1.6 CBOM
   ↓
CLEAR DASHBOARD
```

That chain is the MVP.
