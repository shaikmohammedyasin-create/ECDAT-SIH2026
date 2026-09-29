"""
Binary Scanner — static offline analysis of Java JVM artifacts (.class, .jar).

Implements constant pool inspection of Java bytecode without executing any code.
Detects cryptographic algorithms and API references in compiled binaries.
Includes archive-bomb and path-traversal (Zip Slip) protections.
"""
import io
import os
import struct
import uuid
import zipfile
from typing import List, Set, Tuple

from app.models.crypto_asset import CryptoAsset, AssetType, UsageFunction, QuantumStatus

# Constant pool tags in JVM class file format
TAG_UTF8 = 1
TAG_INTEGER = 3
TAG_FLOAT = 4
TAG_LONG = 5
TAG_DOUBLE = 6
TAG_CLASS = 7
TAG_STRING = 8
TAG_FIELDREF = 9
TAG_METHODREF = 10
TAG_INTERFACEMETHODREF = 11
TAG_NAMEANDTYPE = 12
TAG_METHODHANDLE = 15
TAG_METHODTYPE = 16
TAG_DYNAMIC = 17
TAG_INVOKEDYNAMIC = 18
TAG_MODULE = 19
TAG_PACKAGE = 20

# Known cryptographic APIs and algorithms to inspect in bytecode
KNOWN_CRYPTO_CLASSES = {
    "javax/crypto/Cipher",
    "javax/crypto/KeyGenerator",
    "javax/crypto/KeyAgreement",
    "javax/crypto/SecretKey",
    "javax/crypto/spec/SecretKeySpec",
    "java/security/Signature",
    "java/security/MessageDigest",
    "java/security/KeyPairGenerator",
    "java/security/KeyFactory",
    "org/bouncycastle/crypto",
}

ALGO_INDICATORS = {
    "RSA": (UsageFunction.ENCRYPTION, 2048, "ECDAT-BIN-RSA-001"),
    "DSA": (UsageFunction.SIGNATURE, 1024, "ECDAT-BIN-DSA-001"),
    "ECDSA": (UsageFunction.SIGNATURE, 256, "ECDAT-BIN-ECDSA-001"),
    "ECDH": (UsageFunction.KEY_EXCHANGE, 256, "ECDAT-BIN-ECDH-001"),
    "AES": (UsageFunction.ENCRYPTION, None, "ECDAT-BIN-AES-001"),
    "DES": (UsageFunction.ENCRYPTION, 56, "ECDAT-BIN-DES-001"),
    "DESEDE": (UsageFunction.ENCRYPTION, 112, "ECDAT-BIN-DES3-001"),
    "3DES": (UsageFunction.ENCRYPTION, 112, "ECDAT-BIN-DES3-001"),
    "MD5": (UsageFunction.HASH, None, "ECDAT-BIN-MD5-001"),
    "SHA-1": (UsageFunction.HASH, None, "ECDAT-BIN-SHA1-001"),
    "SHA1": (UsageFunction.HASH, None, "ECDAT-BIN-SHA1-001"),
    "SHA-256": (UsageFunction.HASH, None, "ECDAT-BIN-SHA256-001"),
    "SHA256": (UsageFunction.HASH, None, "ECDAT-BIN-SHA256-001"),
    "SHA-512": (UsageFunction.HASH, None, "ECDAT-BIN-SHA512-001"),
}

MAX_CLASS_SIZE = 10 * 1024 * 1024  # 10 MB per class file
MAX_JAR_ENTRIES = 2000             # Archive bomb protection


def _parse_class_constant_pool(raw_bytes: bytes) -> Set[str]:
    """Statically parse UTF-8 string constants from Java class bytecode."""
    strings = set()
    if len(raw_bytes) < 10:
        return strings

    # Check magic header: 0xCAFEBABE
    magic = raw_bytes[:4]
    if magic != b"\xca\xfe\xba\xbe":
        return strings

    try:
        offset = 8
        cp_count = struct.unpack(">H", raw_bytes[offset:offset + 2])[0]
        offset += 2

        idx = 1
        while idx < cp_count and offset < len(raw_bytes):
            tag = raw_bytes[offset]
            offset += 1

            if tag == TAG_UTF8:
                if offset + 2 > len(raw_bytes):
                    break
                length = struct.unpack(">H", raw_bytes[offset:offset + 2])[0]
                offset += 2
                if offset + length <= len(raw_bytes):
                    val = raw_bytes[offset:offset + length].decode("utf-8", errors="ignore")
                    strings.add(val)
                offset += length
                idx += 1
            elif tag in (TAG_INTEGER, TAG_FLOAT, TAG_FIELDREF, TAG_METHODREF,
                         TAG_INTERFACEMETHODREF, TAG_NAMEANDTYPE, TAG_DYNAMIC, TAG_INVOKEDYNAMIC):
                offset += 4
                idx += 1
            elif tag in (TAG_LONG, TAG_DOUBLE):
                offset += 8
                idx += 2  # 8-byte constants take two entries
            elif tag in (TAG_CLASS, TAG_STRING, TAG_METHODTYPE, TAG_MODULE, TAG_PACKAGE):
                offset += 2
                idx += 1
            elif tag == TAG_METHODHANDLE:
                offset += 3
                idx += 1
            else:
                break
    except Exception:
        pass
    return strings


def scan_class_bytes(raw_bytes: bytes, file_path: str, container_name: str = "") -> List[CryptoAsset]:
    """Scan raw Java bytecode bytes for cryptographic signatures."""
    if len(raw_bytes) > MAX_CLASS_SIZE:
        return []

    strings = _parse_class_constant_pool(raw_bytes)
    if not strings:
        return []

    has_crypto_api = any(cls in s for s in strings for cls in KNOWN_CRYPTO_CLASSES)
    assets = []

    for algo, (usage, ksize, rule_id) in ALGO_INDICATORS.items():
        found = False
        for s in strings:
            s_up = s.upper()
            if s_up == algo or f"/{algo}/" in s_up or f"{algo}/" in s_up or f"/{algo}" in s_up or f"\"{algo}\"" in s_up:
                found = True
                break
            elif has_crypto_api and algo in s_up:
                found = True
                break

        if found:
            canon_algo = "DES3" if algo in ("3DES", "DESEDE") else ("SHA-1" if algo == "SHA1" else ("SHA-256" if algo == "SHA256" else algo))
            display_path = f"{container_name}!/{file_path}" if container_name else file_path
            assets.append(CryptoAsset(
                asset_id=str(uuid.uuid4()),
                asset_type=AssetType.ALGORITHM,
                algorithm=canon_algo,
                primitive=canon_algo,
                key_size=ksize,
                mode=None,
                padding=None,
                curve=None,
                hash_algo=None,
                library="JVM Bytecode",
                file_path=display_path,
                line_number=1,
                source_snippet=f"Bytecode constant reference: {algo} in {os.path.basename(file_path)}",
                confidence="MEDIUM",
                usage=usage,
                rule_id=rule_id,
                provenance="OBSERVED",
                quantum_status=QuantumStatus.SAFE,
                lifetime="L",
                criticality="High",
                exposure="Internal"
            ))
    return assets


def scan_binary_file(filepath: str) -> List[CryptoAsset]:
    """Scan a compiled binary (.class, .jar) statically without execution."""
    ext = os.path.splitext(filepath)[1].lower()
    if ext == ".class":
        try:
            with open(filepath, "rb") as f:
                data = f.read()
            return scan_class_bytes(data, filepath)
        except Exception:
            return []

    elif ext in (".jar", ".war"):
        assets = []
        try:
            with zipfile.ZipFile(filepath, "r") as zf:
                entries = zf.infolist()
                count = 0
                for entry in entries:
                    if count >= MAX_JAR_ENTRIES:
                        break
                    # Zip Slip security check: ignore absolute paths or parent references
                    if entry.filename.startswith(("/", "\\")) or ".." in entry.filename:
                        continue
                    if entry.filename.lower().endswith(".class"):
                        count += 1
                        try:
                            class_bytes = zf.read(entry)
                            assets.extend(scan_class_bytes(class_bytes, entry.filename, os.path.basename(filepath)))
                        except Exception:
                            continue
        except Exception:
            pass
        return assets

    return []
