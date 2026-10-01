# Enterprise Cryptographic Discovery & Analysis Tool (ECDAT)
**Problem Statement:** 26164 · **Org:** NTRO · **Theme:** Blockchain & Cybersecurity

---

## STATUS REPORT & PRIORITISED TASK LIST (from repository audit)

### CURRENTLY WORKING
- `app/models/crypto_asset.py` — Pydantic `CryptoAsset` model
- `app/scanners/source_scanner.py` — regex source scanner (Python/Java/JS). **Verified:** 33 findings on `test-data/sample-project`
- `app/analysis/quantum_rules.py` — Shor/Grover/legacy classification + HNDL/TNFL
- `app/analysis/mosca.py` — Mosca `X+Y>Z` engine
- `app/analysis/recommendations.py` — deterministic PQC/hybrid recommendations
- `app/cbom/cyclonedx.py` — CycloneDX 1.6 CBOM generation (no validation yet)
- `app/ui/dashboard.py` — Streamlit single-page dashboard
- `scanners/certificate_scanner.py` — X.509 parser (was silent because `cryptography` was missing; now installed)

### PARTIALLY WORKING / GAPS vs source-of-truth
| Area | Status | Source-of-truth requirement |
|---|---|---|
| Dependency scanner | **MISSING** | Parse `requirements.txt` + `pom.xml`, capture lib/version |
| Config/IaC scanner | **MISSING** | nginx.conf / sshd_config / TLS config detection |
| CBOM schema validation | **MISSING** | Validate against CycloneDX 1.6 JSON schema |
| Tests | **MISSING** (`tests/` empty) | Tests for every P0 acceptance gate |
| Controlled corpus w/ expected findings | **PARTIAL** | Planted examples + `expected_findings.json` |
| Risk score formula | **WRONG** | Uses 40/30/15/15; source-of-truth = 35/25/15/15/10 |
| Data model fields | **PARTIAL** | Missing data_sensitivity/lifetime_years/business_criticality/component_ref |
| Certificate scanning | **UNBLOCKED** | `cryptography` now installed |

### BLOCKERS
- None. (`cryptography` interdependency resolved.)

### PRIORITISED TASK LIST (P0 order)
1. **P0** Dependency scanner (`requirements.txt` + `pom.xml`) + add `pom.xml` to corpus
2. **P0** Configuration/IaC scanner (nginx/TLS/sshd)
3. **P0** Fix risk score → source-of-truth 35/25/15/15/10 formula
4. **P0** Extend CryptoAsset model with source-of-truth fields
5. **P0** CBOM generation upgrade + real CycloneDX 1.6 schema validation
6. **P0** Build controlled corpus + `expected_findings.json`
7. **P0** Write & run the full test suite
8. **P0** Multi-page Streamlit dashboard (Dashboard / Inventory / Asset Detail / Mosca Simulator / Reports)
9. **P0** Measure real metrics + generate evidence screenshots

**Decision input (Laya):** task=TRUE · priority=HIGH · urgency=1.0 · importance=1.0 · action=DO_NOW. Proceeding autonomously on P0.
