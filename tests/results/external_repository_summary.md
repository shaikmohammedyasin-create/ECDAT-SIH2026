# ECDAT External Repositories Validation Summary

**Evaluation Date:** `2026-09-30T04:32:49.647519+00:00`  
**External Targets Evaluated:** OpenSSL, CPython, OpenSSH Portable (All pinned via `manifest.json`)

---

## 1. Comparative Benchmark Table

| Repository | Tag           | Commit     | Files | Duration | Findings | CBOM 1.6       | Status |
|------------|---------------|------------|-------|----------|----------|----------------|--------|
| openssl    | openssl-3.3.0 | 4cb31128b5 | 5,295 | 7.983s   | 1295     | 0 errs (VALID) | PASS   |
| cpython    | v3.12.3       | f6650f9ad7 | 4,636 | 27.359s  | 45       | 0 errs (VALID) | PASS   |
| openssh    | V_9_7_P1      | 86bdd3853f | 849   | 0.956s   | 205      | 0 errs (VALID) | PASS   |

---

## 2. Key Observations & Robustness Takeaways

1. **OpenSSL (`openssl-3.3.0`):**
   * Cryptography-heavy codebase discovering `1295` assets in `7.983s`.
   * High density of `EVP_` interfaces, RSA/ECDSA/AES instances, and X.509 certificates.
   * Generated CycloneDX 1.6 CBOM with 0 schema errors.

2. **CPython (`v3.12.3`):**
   * Large Python standard library repository (4,636 files).
   * Rejection of arbitrary text tokens prevented regex explosion.
   * AST call-site extraction precisely identified `hashlib` and `ssl` invocations.

3. **OpenSSH Portable (`V_9_7_P1`):**
   * High precision on SSH key exchange protocols (`curve25519-sha256`, `ssh-ed25519`, `ssh-rsa`).
   * Scanned in `0.956s` with 0 CBOM validation errors.
