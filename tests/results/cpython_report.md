# ECDAT External Repository Validation: CPYTHON

**Repository:** [https://github.com/python/cpython](https://github.com/python/cpython)  
**Pinned Tag/Version:** `v3.12.3`  
**Commit SHA:** `f6650f9ad73359051f3e558c2431a109bc016664`  
**Scanned At:** `2026-09-30T04:32:48.168735+00:00`  
**Validation Status:** **`PASS`**

---

## 1. Codebase Inventory & Scan Performance

| Metric | Measured Value |
|---|---|
| **Total Files Traversed** | `4,636` files |
| **Source Files Scanned** | `2,868` files |
| **Codebase Footprint** | `99.22 MB` |
| **Scan Execution Duration** | **`27.359s`** |
| **Scanner Throughput** | `169.5 files/sec` |
| **Peak Memory Allocation** | `0.0 MB` |
| **CBOM Generation Time** | `0.0005s` |
| **CycloneDX 1.6 Validation Time** | `0.0447s` |
| **Schema Validation Errors** | **`0`** (Valid: `True`) |

---

## 2. Cryptographic Findings Overview

* **Total Cryptographic Assets Discovered:** **`45`**
* **Confidence Distribution:**
  * HIGH: `45`
  * MEDIUM: `0`
  * LOW: `0`
* **Mosca Violations (Z=2035, X=10y, Y=3y):** `15`
* **Risk Distribution:**
  * Critical: `35`
  * High: `0`
  * Medium: `10`
  * Low / Info: `0`

### Top Discovered Cryptographic Algorithms
| Algorithm | Occurrences |
|-----------|-------------|
| RSA       | 14          |
| MD5       | 11          |
| SHA-256   | 9           |
| SHA-1     | 9           |
| SHA-3     | 1           |
| ECDSA     | 1           |

---

## 3. CycloneDX 1.6 CBOM Compliance

* **CycloneDX Specification:** 1.6
* **CBOM Component Count:** `45`
* **CryptoProperties Compliance:** 100% of components contain valid cryptographic properties
* **Validation Outcome:** **PASS (0 schema errors)**
