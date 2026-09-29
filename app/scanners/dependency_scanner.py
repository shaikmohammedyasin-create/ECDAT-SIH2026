"""
Dependency Scanner — parses multi-ecosystem dependency manifests and emits crypto-relevant Library assets.

Supported inputs:
  - requirements.txt, requirements-dev.txt (Python)
  - pyproject.toml                         (Python)
  - pom.xml                                (Java/Maven)
  - package.json, package-lock.json        (Node.js/npm)
  - go.mod                                 (Go)
  - Cargo.toml                             (Rust)

Detects: package name, version, crypto relevance, algorithm, and primitive.
Security: Reads manifest text offline; never executes or fetches packages from the network.
"""
import json
import os
import re
import uuid
from typing import List, Tuple, Optional

try:
    import defusedxml.ElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

from app.models.crypto_asset import CryptoAsset, AssetType, UsageFunction, QuantumStatus

# Known crypto library -> (primitive, algorithm, usage)
CRYPTO_LIBS = {
    # PyPI
    "pycryptodome":       ("algorithm", "AES", UsageFunction.ENCRYPTION),
    "cryptography":       ("algorithm", "RSA", UsageFunction.ENCRYPTION),
    "rsa":                ("algorithm", "RSA", UsageFunction.ENCRYPTION),
    "ecdsa":              ("algorithm", "ECDSA", UsageFunction.SIGNATURE),
    "pyopenssl":          ("protocol", "TLS", UsageFunction.KEY_EXCHANGE),
    "pyca/cryptography":  ("algorithm", "RSA", UsageFunction.ENCRYPTION),
    "bouncycastle":       ("algorithm", "RSA", UsageFunction.ENCRYPTION),
    "bcprov-jdk18on":     ("algorithm", "RSA", UsageFunction.ENCRYPTION),
    "bcprov-jdk15on":     ("algorithm", "RSA", UsageFunction.ENCRYPTION),
    "bcprov":             ("algorithm", "RSA", UsageFunction.ENCRYPTION),
    "openssl":            ("protocol", "TLS", UsageFunction.KEY_EXCHANGE),
    "bcrypt":             ("algorithm", "BCRYPT", UsageFunction.HASH),
    "argon2-cffi":        ("algorithm", "ARGON2", UsageFunction.HASH),
    "libsodium":          ("algorithm", "X25519", UsageFunction.KEY_EXCHANGE),
    "pynacl":             ("algorithm", "X25519", UsageFunction.KEY_EXCHANGE),
    "jose":               ("algorithm", "ECDSA", UsageFunction.SIGNATURE),
    "python-jose":        ("algorithm", "ECDSA", UsageFunction.SIGNATURE),
    "nimbus-jose-jwt":    ("algorithm", "RSA", UsageFunction.SIGNATURE),
    "jjwt":               ("algorithm", "RSA", UsageFunction.SIGNATURE),
    "tink":               ("algorithm", "AES", UsageFunction.ENCRYPTION),

    # npm
    "node-forge":         ("algorithm", "RSA", UsageFunction.ENCRYPTION),
    "crypto-js":          ("algorithm", "AES", UsageFunction.ENCRYPTION),
    "bcryptjs":           ("algorithm", "BCRYPT", UsageFunction.HASH),
    "jsonwebtoken":       ("algorithm", "RSA", UsageFunction.SIGNATURE),
    "tweetnacl":          ("algorithm", "Ed25519", UsageFunction.SIGNATURE),
    "elliptic":           ("algorithm", "ECDSA", UsageFunction.SIGNATURE),

    # Go
    "golang.org/x/crypto": ("algorithm", "Ed25519", UsageFunction.SIGNATURE),
    "crypto/tls":          ("protocol", "TLS", UsageFunction.KEY_EXCHANGE),

    # Cargo / Rust
    "ring":               ("algorithm", "AES", UsageFunction.ENCRYPTION),
    "ed25519-dalek":      ("algorithm", "Ed25519", UsageFunction.SIGNATURE),
    "aes-gcm":            ("algorithm", "AES", UsageFunction.ENCRYPTION),
}

QUANTUM_SAFE_LIBS = {"sha3", "pycryptodomex", "sphincs", "pqcrypto", "liboqs", "oqs"}
NEUTRAL_LIBS = {"fastapi", "uvicorn", "flask", "django", "requests", "gunicorn", "express"}


def _parse_requirements(path: str) -> List[Tuple[str, Optional[str]]]:
    out = []
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or line.startswith("-"):
                    continue
                line = re.split(r"\s*(?:;|#)\s*", line, maxsplit=1)[0].strip()
                m = re.match(r"^([A-Za-z0-9_.\-\[\]]+)\s*(?:==|>=|<=|~=|!=|=)?\s*([\w.\-]+)?", line)
                if not m:
                    continue
                name = m.group(1).lstrip(".").lower()
                if "[" in name:
                    name = name[: name.index("[")]
                ver = m.group(2) or None
                out.append((name, ver))
    except Exception:
        pass
    return out


def _parse_pom(path: str) -> List[Tuple[str, Optional[str]]]:
    out = []
    try:
        tree = ET.parse(path)
        root = tree.getroot()
        for dep in root.findall(".//{*}dependency"):
            g = dep.findtext("{*}groupId") or dep.findtext("groupId") or ""
            a = dep.findtext("{*}artifactId") or dep.findtext("artifactId") or ""
            v = dep.findtext("{*}version") or dep.findtext("version")
            if g or a:
                out.append((f"{g}:{a}".lower(), v))
    except Exception:
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                txt = f.read()
            for m in re.finditer(r"<artifactId>([^<]+)</artifactId>\s*(?:<version>([^<]+)</version>)?", txt):
                out.append((m.group(1).strip().lower(), (m.group(2) or None)))
        except Exception:
            pass
    return out


def _parse_json_deps(path: str) -> List[Tuple[str, Optional[str]]]:
    out = []
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            data = json.load(f)
        for key in ("dependencies", "devDependencies"):
            for pkg, ver in (data.get(key) or {}).items():
                v_clean = str(ver).lstrip("^~") if ver else None
                out.append((pkg.lower(), v_clean))
    except Exception:
        pass
    return out


def _parse_toml_deps(path: str) -> List[Tuple[str, Optional[str]]]:
    out = []
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                # Format 1: Quoted list item e.g. "cryptography>=41.0.0",
                m_arr = re.match(r'^["\']([A-Za-z0-9_.\-\[\]]+)\s*(?:==|>=|<=|~=|!=|=)?\s*([\w.\-]+)?["\']?,?', line)
                if m_arr and m_arr.group(1) not in ("project", "tool", "dependencies"):
                    pkg = m_arr.group(1).lower()
                    if "[" in pkg:
                        pkg = pkg[: pkg.index("[")]
                    out.append((pkg, m_arr.group(2) or None))
                    continue

                # Format 2: Key = value e.g. ring = "0.17" or pycryptodome = { version = "..." }
                m = re.match(r'^([A-Za-z0-9_.\-]+)\s*=\s*[\{"]?\s*(?:version\s*=\s*)?"?([0-9][\w.\-]*)?', line)
                if m:
                    out.append((m.group(1).lower(), m.group(2) or None))
    except Exception:
        pass
    return out


def _parse_go_mod(path: str) -> List[Tuple[str, Optional[str]]]:
    out = []
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith(("//", "module", "go ")):
                    continue
                parts = line.split()
                if len(parts) >= 2:
                    out.append((parts[0].lower(), parts[1]))
    except Exception:
        pass
    return out


def _create_dep_assets(
    deps: List[Tuple[str, Optional[str]]],
    file_path: str,
    eco_rule_id: str,
) -> List[CryptoAsset]:
    assets = []
    for name, ver in deps:
        base = name.split(":")[-1]
        match_key = base
        if match_key not in CRYPTO_LIBS:
            match_key = name
        if match_key in CRYPTO_LIBS:
            primitive, algo, usage = CRYPTO_LIBS[match_key]
        elif base in QUANTUM_SAFE_LIBS or name in QUANTUM_SAFE_LIBS:
            primitive, algo, usage = ("algorithm", name.split(":")[-1].upper(), UsageFunction.HASH)
        elif base in NEUTRAL_LIBS or name in NEUTRAL_LIBS:
            continue
        else:
            continue

        assets.append(CryptoAsset(
            asset_id=str(uuid.uuid4()),
            asset_type=AssetType.LIBRARY,
            algorithm=algo,
            primitive=primitive,
            key_size=None,
            mode=None,
            padding=None,
            curve=None,
            hash_algo=None,
            library=base,
            file_path=file_path,
            line_number=1,
            source_snippet=f"{base}=={ver}" if ver else base,
            confidence="MEDIUM",
            usage=usage,
            rule_id=eco_rule_id,
            provenance="OBSERVED",
            quantum_status=QuantumStatus.VULNERABLE if algo in ("RSA", "ECDSA", "X25519") else QuantumStatus.SAFE,
            lifetime="M",
            criticality="Med",
            exposure="Internal",
        ))
    return assets


def scan_dependency_file(filepath: str) -> List[CryptoAsset]:
    base = os.path.basename(filepath).lower()
    if base in ("requirements.txt", "requirements-dev.txt"):
        return _create_dep_assets(_parse_requirements(filepath), filepath, "ECDAT-DEP-PY-001")
    elif base == "pom.xml":
        return _create_dep_assets(_parse_pom(filepath), filepath, "ECDAT-DEP-JAVA-001")
    elif base in ("package.json", "package-lock.json"):
        return _create_dep_assets(_parse_json_deps(filepath), filepath, "ECDAT-DEP-NPM-001")
    elif base in ("pyproject.toml", "cargo.toml"):
        rule = "ECDAT-DEP-PY-001" if "pyproject" in base else "ECDAT-DEP-RUST-001"
        return _create_dep_assets(_parse_toml_deps(filepath), filepath, rule)
    elif base in ("go.mod", "go.sum"):
        return _create_dep_assets(_parse_go_mod(filepath), filepath, "ECDAT-DEP-GO-001")
    return []
