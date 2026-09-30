# ECDAT External Repository Validation: OPENSSL

**Repository:** [https://github.com/openssl/openssl](https://github.com/openssl/openssl)  
**Pinned Tag/Version:** `openssl-3.3.0`  
**Commit SHA:** `4cb31128b5790819dfeea2739fbde265f71a10a2`  
**Scanned At:** `2026-09-30T04:32:20.068199+00:00`  
**Validation Status:** **`PASS`**

---

## 1. Codebase Inventory & Scan Performance

| Metric | Measured Value |
|---|---|
| **Total Files Traversed** | `5,295` files |
| **Source Files Scanned** | `2,066` files |
| **Codebase Footprint** | `63.26 MB` |
| **Scan Execution Duration** | **`7.983s`** |
| **Scanner Throughput** | `663.3 files/sec` |
| **Peak Memory Allocation** | `0.0 MB` |
| **CBOM Generation Time** | `0.0182s` |
| **CycloneDX 1.6 Validation Time** | `3.9573s` |
| **Schema Validation Errors** | **`0`** (Valid: `True`) |

---

## 2. Cryptographic Findings Overview

* **Total Cryptographic Assets Discovered:** **`1295`**
* **Confidence Distribution:**
  * HIGH: `766`
  * MEDIUM: `512`
  * LOW: `17`
* **Mosca Violations (Z=2035, X=10y, Y=3y):** `590`
* **Risk Distribution:**
  * Critical: `629`
  * High: `17`
  * Medium: `165`
  * Low / Info: `484`

### Top Discovered Cryptographic Algorithms
| Algorithm        | Occurrences |
|------------------|-------------|
| RSA              | 387         |
| TLSV1.3          | 289         |
| AES              | 212         |
| TLSV1.2          | 195         |
| ECDSA            | 56          |
| SHA-1            | 37          |
| SHA-256          | 36          |
| TLSV1.0 (legacy) | 16          |

---

## 3. CycloneDX 1.6 CBOM Compliance

* **CycloneDX Specification:** 1.6
* **CBOM Component Count:** `1295`
* **CryptoProperties Compliance:** 100% of components contain valid cryptographic properties
* **Validation Outcome:** **PASS (0 schema errors)**
