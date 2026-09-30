# ECDAT External Repository Validation: OPENSSH

**Repository:** [https://github.com/openssh/openssh-portable](https://github.com/openssh/openssh-portable)  
**Pinned Tag/Version:** `V_9_7_P1`  
**Commit SHA:** `86bdd3853f4d32c85e295e6216a2fe0953ad93f0`  
**Scanned At:** `2026-09-30T02:17:36.887648+00:00`  
**Validation Status:** **`PASS`**

---

## 1. Codebase Inventory & Scan Performance

| Metric | Measured Value |
|---|---|
| **Total Files Traversed** | `849` files |
| **Source Files Scanned** | `411` files |
| **Codebase Footprint** | `6.66 MB` |
| **Scan Execution Duration** | **`1.938s`** |
| **Scanner Throughput** | `438.1 files/sec` |
| **Peak Memory Allocation** | `0.0 MB` |
| **CBOM Generation Time** | `0.0056s` |
| **CycloneDX 1.6 Validation Time** | `0.9831s` |
| **Schema Validation Errors** | **`0`** (Valid: `True`) |

---

## 2. Cryptographic Findings Overview

* **Total Cryptographic Assets Discovered:** **`205`**
* **Confidence Distribution:**
  * HIGH: `204`
  * MEDIUM: `1`
  * LOW: `0`
* **Mosca Violations (Z=2035, X=10y, Y=3y):** `191`
* **Risk Distribution:**
  * Critical: `193`
  * High: `0`
  * Medium: `12`
  * Low / Info: `0`

### Top Discovered Cryptographic Algorithms
| Algorithm | Occurrences |
|-----------|-------------|
| RSA       | 90          |
| ECDSA     | 38          |
| Ed25519   | 34          |
| AES       | 16          |
| DSA       | 12          |
| X25519    | 6           |
| ChaCha20  | 2           |
| SHA-256   | 2           |

---

## 3. CycloneDX 1.6 CBOM Compliance

* **CycloneDX Specification:** 1.6
* **CBOM Component Count:** `205`
* **CryptoProperties Compliance:** 100% of components contain valid cryptographic properties
* **Validation Outcome:** **PASS (0 schema errors)**
