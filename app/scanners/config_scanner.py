"""
Configuration / IaC Scanner — detects cryptographic configuration in config files.

P0 targets:
  - nginx.conf / TLS config (server blocks)
  - sshd_config
  - openssl.cnf
  - Dockerfile / docker-compose (crypto-related ENV/commands)

Detects:
  - TLS protocol versions
  - cipher suites (and whether they reference RSA/ECDSA/AES/DES)
  - key-exchange requirements (ssl_dhparam, ECDHE/DHE)
  - certificate references
  - weak/legacy TLS cipher indicators

Static analysis only — never connects to any endpoint.
"""
import os
import re
import uuid
from typing import List

from app.models.crypto_asset import CryptoAsset, AssetType, UsageFunction, QuantumStatus

# Weak/legacy ciphers we can confidently flag (source-of-truth weak/legacy list).
WEAK_CIPHER_HINTS = {
    "DES": ("DES", "encryption", True),
    "RC4": ("RC4", "encryption", True),
    "MD5": ("MD5", "hash", True),
    "SHA1": ("SHA-1", "hash", True),
    "3DES": ("DES3", "encryption", True),
    "CBC-SHA": ("AES", "encryption", False),
}

# TLS versions -> protocol assets
TLS_VERSION_PATTERN = re.compile(r"TLSv(1\.0|1\.1|1\.2|1\.3)", re.IGNORECASE)

RSA_CIPHER = re.compile(r"(ECDHE|DHE|RSA|AES128|AES256)-RSA", re.IGNORECASE)
ECDSA_CIPHER = re.compile(r"-ECDSA", re.IGNORECASE)
AES_CIPHER = re.compile(r"AES\d+", re.IGNORECASE)


def _mk(algorithm, usage, key_size, file_path, line_number, snippet, confidence,
        quantum, exposure="Internal", criticality="Med", source="config_scanner",
        rule_id: str = "ECDAT-CFG-GEN-001") -> CryptoAsset:
    return CryptoAsset(
        asset_id=str(uuid.uuid4()),
        asset_type=AssetType.PROTOCOL,
        algorithm=algorithm,
        primitive=algorithm,
        key_size=key_size,
        mode=None,
        padding=None,
        curve=None,
        hash_algo=None,
        library="config",
        file_path=file_path,
        line_number=line_number,
        source_snippet=snippet[:200],
        confidence=confidence,
        usage=usage,
        rule_id=rule_id,
        quantum_status=quantum,
        lifetime="M",
        criticality=criticality,
        exposure=exposure,
    )


def scan_config_file(filepath: str) -> List[CryptoAsset]:
    assets = []
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            data = f.read()
    except Exception:
        return []
    lines = data.splitlines()
    base = os.path.basename(filepath).lower()

    # --- TLS version detection (nginx/TLS configs) ---
    for idx, line in enumerate(lines, start=1):
        clean_line = line.strip()
        if clean_line.startswith(("#", "//", ";")):
            continue
        m = TLS_VERSION_PATTERN.search(clean_line)
        if m and ("ssl_protocols" in clean_line or "tls" in base or "nginx" in base or "ssl" in clean_line.lower()):
            ver = m.group(0).upper()
            legacy = ver in ("TLSV1.0", "TLSV1.1")
            assets.append(_mk(
                ver if not legacy else f"{ver} (legacy)",
                UsageFunction.KEY_EXCHANGE,
                None, filepath, idx, clean_line,
                "HIGH" if legacy else "MEDIUM",
                QuantumStatus.LEGACY_BROKEN if legacy else QuantumStatus.SAFE,
                criticality="High" if legacy else "Med",
                rule_id="ECDAT-CFG-TLS-001" if not legacy else "ECDAT-CFG-TLS-LEGACY",
            ))

    # --- Cipher suite detection ---
    for idx, line in enumerate(lines, start=1):
        clean_line = line.strip()
        # Ignore comments to prevent comment text from prematurely breaking out
        if clean_line.startswith(("#", "//", ";")):
            continue
        if "ssl_ciphers" in clean_line or "ciphers" in clean_line.lower():
            found_any = False
            for hint, (algo, _usage, weak) in WEAK_CIPHER_HINTS.items():
                if hint in clean_line.upper():
                    assets.append(_mk(
                        algo, UsageFunction.ENCRYPTION, 128 if algo in ("AES", "DES") else None,
                        filepath, idx, clean_line,
                        "HIGH" if weak else "MEDIUM",
                        QuantumStatus.LEGACY_BROKEN if weak else QuantumStatus.WEAKENED,
                        criticality="High" if weak else "Medium",
                        rule_id=f"ECDAT-CFG-CIPHER-{algo}",
                    ))
                    found_any = True
            if RSA_CIPHER.search(clean_line):
                assets.append(_mk("RSA", UsageFunction.KEY_EXCHANGE, 2048, filepath, idx,
                                  clean_line, "MEDIUM", QuantumStatus.VULNERABLE, criticality="High",
                                  rule_id="ECDAT-CFG-CIPHER-RSA"))
                found_any = True
            if ECDSA_CIPHER.search(clean_line):
                assets.append(_mk("ECDSA", UsageFunction.SIGNATURE, 256, filepath, idx,
                                  clean_line, "MEDIUM", QuantumStatus.VULNERABLE, criticality="High",
                                  rule_id="ECDAT-CFG-CIPHER-ECDSA"))
                found_any = True
            if AES_CIPHER.search(clean_line):
                assets.append(_mk("AES", UsageFunction.ENCRYPTION, None, filepath, idx,
                                  clean_line, "LOW", QuantumStatus.WEAKENED,
                                  rule_id="ECDAT-CFG-CIPHER-AES"))
                found_any = True
            if found_any:
                break  # successfully captured cipher configuration directive

    # --- Certificate references ---
    for idx, line in enumerate(lines, start=1):
        clean_line = line.strip()
        if clean_line.startswith(("#", "//", ";")):
            continue
        if re.search(r"ssl_certificate\b", clean_line):
            assets.append(_mk("X.509", UsageFunction.SIGNATURE, None, filepath, idx,
                              clean_line, "MEDIUM", QuantumStatus.VULNERABLE,
                              criticality="High", source="config_scanner",
                              rule_id="ECDAT-CFG-CERT-001"))

    # --- DH parameters ---
    for idx, line in enumerate(lines, start=1):
        clean_line = line.strip()
        if clean_line.startswith(("#", "//", ";")):
            continue
        m = re.search(r"ssl_dhparam\b[^\n]*?(\d{3,5})", clean_line)
        if m:
            ks = int(m.group(1))
            assets.append(_mk("DH", UsageFunction.KEY_EXCHANGE, ks, filepath, idx,
                              clean_line, "MEDIUM", QuantumStatus.VULNERABLE,
                              criticality="High", source="config_scanner",
                              rule_id="ECDAT-CFG-DH-001"))

    return assets
