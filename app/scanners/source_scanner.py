import ast
import os
import re
import uuid
from typing import List, Tuple
from app.models.crypto_asset import CryptoAsset, AssetType, UsageFunction, QuantumStatus

# Standardized Regex patterns for high value targets with deterministic ECDAT-SRC rule IDs
PATTERNS = {
    # Asymmetric
    "RSA": [
        (r"(?i)RSA\.generate\((\d+)\)", "HIGH", UsageFunction.ENCRYPTION, lambda m: int(m.group(1)), "ECDAT-SRC-RSA-001"),
        (r"(?i)KeyPairGenerator\.getInstance\(\"RSA\"\).*?initialize\((\d+)\)", "HIGH", UsageFunction.ENCRYPTION, lambda m: int(m.group(1)), "ECDAT-SRC-JAVA-RSA-001"),
        (r"(?i)KeyPairGenerator\.getInstance\(\"RSA\"\)", "MEDIUM", UsageFunction.ENCRYPTION, lambda m: 2048, "ECDAT-SRC-JAVA-RSA-002"),
        (r"(?i)Cipher\.getInstance\(\"RSA[^\"]*\"\)", "HIGH", UsageFunction.ENCRYPTION, lambda m: 2048, "ECDAT-SRC-JAVA-RSA-003"),
        (r"(?i)RS(256|384|512)", "HIGH", UsageFunction.SIGNATURE, lambda m: 2048, "ECDAT-SRC-JS-RSA-001"),
        (r"(?i)\bEVP_PKEY_RSA\b|\bRSA_new\b|\bRSA_generate_key\b", "HIGH", UsageFunction.ENCRYPTION, lambda m: 2048, "ECDAT-SRC-C-RSA-001"),
        (r"(?i)\bssh-rsa\b|\brsa-sha2-256\b|\brsa-sha2-512\b", "HIGH", UsageFunction.SIGNATURE, lambda m: 2048, "ECDAT-SRC-SSH-RSA-001"),
    ],
    "DSA": [
        (r"(?i)Signature\.getInstance\(\"SHA1withDSA\"\)", "HIGH", UsageFunction.SIGNATURE, lambda m: None, "ECDAT-SRC-JAVA-DSA-001"),
        (r"(?i)KeyPairGenerator\.getInstance\(\"DSA\"\)", "HIGH", UsageFunction.SIGNATURE, lambda m: 1024, "ECDAT-SRC-JAVA-DSA-002"),
    ],
    "ECDSA": [
        (r"(?i)KeyPairGenerator\.getInstance\(\"(EC|ECDSA)\"\)", "MEDIUM", UsageFunction.SIGNATURE, lambda m: 256, "ECDAT-SRC-JAVA-EC-001"),
        (r"(?i)Signature\.getInstance\(\"[^\"]*withECDSA\"\)", "HIGH", UsageFunction.SIGNATURE, lambda m: 256, "ECDAT-SRC-JAVA-ECDSA-001"),
        (r"(?i)\bSECP256R1\b|\bsecp256k1\b|\bprime256v1\b", "MEDIUM", UsageFunction.SIGNATURE, lambda m: 256, "ECDAT-SRC-PY-EC-001"),
        (r"(?i)\bec\.generate_private_key\b", "HIGH", UsageFunction.SIGNATURE, lambda m: 256, "ECDAT-SRC-PY-EC-002"),
        (r"(?i)\becdsa-sha2-nistp256\b|\becdsa-sha2-nistp384\b", "HIGH", UsageFunction.SIGNATURE, lambda m: 256, "ECDAT-SRC-SSH-ECDSA-001"),
    ],
    "ECDH": [
        (r"(?i)createECDH\('([^']+)'\)", "HIGH", UsageFunction.KEY_EXCHANGE, lambda m: 256, "ECDAT-SRC-JS-ECDH-001"),
        (r"(?i)KeyAgreement\.getInstance\(\"ECDH\"\)", "HIGH", UsageFunction.KEY_EXCHANGE, lambda m: 256, "ECDAT-SRC-JAVA-ECDH-001"),
    ],
    "DH": [
        (r"(?i)KeyAgreement\.getInstance\(\"DH\"\)", "HIGH", UsageFunction.KEY_EXCHANGE, lambda m: 2048, "ECDAT-SRC-JAVA-DH-001"),
        (r"(?i)KeyPairGenerator\.getInstance\(\"DiffieHellman\"\)", "HIGH", UsageFunction.KEY_EXCHANGE, lambda m: 2048, "ECDAT-SRC-JAVA-DH-002"),
    ],
    "X25519": [
        (r"(?i)\bx25519\.X25519PrivateKey\.generate\b", "HIGH", UsageFunction.KEY_EXCHANGE, lambda m: 256, "ECDAT-SRC-PY-X25519-001"),
        (r"(?i)KeyPairGenerator\.getInstance\(\"X25519\"\)", "HIGH", UsageFunction.KEY_EXCHANGE, lambda m: 256, "ECDAT-SRC-JAVA-X25519-001"),
        (r"(?i)\bcurve25519-sha256\b", "HIGH", UsageFunction.KEY_EXCHANGE, lambda m: 256, "ECDAT-SRC-SSH-X25519-001"),
    ],
    "Ed25519": [
        (r"(?i)\bed25519\.Ed25519PrivateKey\.generate\b", "HIGH", UsageFunction.SIGNATURE, lambda m: 256, "ECDAT-SRC-PY-ED25519-001"),
        (r"(?i)KeyPairGenerator\.getInstance\(\"Ed25519\"\)", "HIGH", UsageFunction.SIGNATURE, lambda m: 256, "ECDAT-SRC-JAVA-ED25519-001"),
        (r"(?i)\bssh-ed25519\b", "HIGH", UsageFunction.SIGNATURE, lambda m: 256, "ECDAT-SRC-SSH-ED25519-001"),
    ],
    # Symmetric
    "AES": [
        (r"(?i)AES\.new\([^,]+,\s*AES\.MODE_([A-Z]+)", "HIGH", UsageFunction.ENCRYPTION, lambda m: None, "ECDAT-SRC-AES-001"),
        (r"(?i)createCipheriv\('aes-(\d+)-([a-z]+)'", "HIGH", UsageFunction.ENCRYPTION, lambda m: int(m.group(1)), "ECDAT-SRC-JS-AES-001"),
        (r"(?i)\"AES/([A-Z]+)/([a-zA-Z]+)\"", "HIGH", UsageFunction.ENCRYPTION, lambda m: None, "ECDAT-SRC-JAVA-AES-001"),
        (r"(?i)\"AES\"", "MEDIUM", UsageFunction.ENCRYPTION, lambda m: None, "ECDAT-SRC-JAVA-AES-002"),
        (r"(?i)\bEVP_aes_(\d+)_\w+\b", "HIGH", UsageFunction.ENCRYPTION, lambda m: int(m.group(1)), "ECDAT-SRC-C-AES-001"),
        (r"(?i)\baes(128|256)-(ctr|gcm|cbc)\b", "HIGH", UsageFunction.ENCRYPTION, lambda m: int(m.group(1)), "ECDAT-SRC-SSH-AES-001"),
    ],
    "DES3": [
        (r"(?i)DES3\.new", "HIGH", UsageFunction.ENCRYPTION, lambda m: 112, "ECDAT-SRC-DES3-001"),
        (r"(?i)createCipheriv\('des-ede3", "HIGH", UsageFunction.ENCRYPTION, lambda m: 112, "ECDAT-SRC-JS-DES3-001"),
        (r"(?i)\"DESede/([A-Z]+)/([a-zA-Z]+)\"", "HIGH", UsageFunction.ENCRYPTION, lambda m: 112, "ECDAT-SRC-JAVA-DES3-001"),
        (r"(?i)\"DESede\"", "MEDIUM", UsageFunction.ENCRYPTION, lambda m: 112, "ECDAT-SRC-JAVA-DES3-002"),
    ],
    "DES": [
        (r"(?i)\"DES/([A-Z]+)/([a-zA-Z]+)\"", "HIGH", UsageFunction.ENCRYPTION, lambda m: 56, "ECDAT-SRC-JAVA-DES-001"),
        (r"(?i)\"DES\"", "MEDIUM", UsageFunction.ENCRYPTION, lambda m: 56, "ECDAT-SRC-JAVA-DES-002"),
        (r"(?i)DES\.new\b", "HIGH", UsageFunction.ENCRYPTION, lambda m: 56, "ECDAT-SRC-PY-DES-001"),
    ],
    "RC4": [
        (r"(?i)ARC4\.new\b", "HIGH", UsageFunction.ENCRYPTION, lambda m: 128, "ECDAT-SRC-RC4-001"),
        (r"(?i)Cipher\.getInstance\(\"(RC4|ARCFOUR)[^\"]*\"\)", "HIGH", UsageFunction.ENCRYPTION, lambda m: 128, "ECDAT-SRC-JAVA-RC4-001"),
        (r"(?i)createCipheriv\('(rc4|arcfour)", "HIGH", UsageFunction.ENCRYPTION, lambda m: 128, "ECDAT-SRC-JS-RC4-001"),
    ],
    "ChaCha20": [
        (r"(?i)ChaCha20(_Poly1305)?\.new\b", "HIGH", UsageFunction.ENCRYPTION, lambda m: 256, "ECDAT-SRC-CHACHA-001"),
        (r"(?i)Cipher\.getInstance\(\"ChaCha20[^\"]*\"\)", "HIGH", UsageFunction.ENCRYPTION, lambda m: 256, "ECDAT-SRC-JAVA-CHACHA-001"),
        (r"(?i)createCipheriv\('chacha20", "HIGH", UsageFunction.ENCRYPTION, lambda m: 256, "ECDAT-SRC-JS-CHACHA-001"),
        (r"(?i)\bchacha20-poly1305\b", "HIGH", UsageFunction.ENCRYPTION, lambda m: 256, "ECDAT-SRC-SSH-CHACHA-001"),
    ],
    # Hash
    "SHA-256": [
        (r"(?i)hashlib\.sha256", "HIGH", UsageFunction.HASH, lambda m: None, "ECDAT-SRC-SHA256-001"),
        (r"(?i)MessageDigest\.getInstance\(\"SHA-256\"\)", "HIGH", UsageFunction.HASH, lambda m: None, "ECDAT-SRC-JAVA-SHA256-001"),
        (r"(?i)createHash\('sha256'\)", "HIGH", UsageFunction.HASH, lambda m: None, "ECDAT-SRC-JS-SHA256-001"),
        (r"(?i)\bEVP_sha256\b", "HIGH", UsageFunction.HASH, lambda m: None, "ECDAT-SRC-C-SHA256-001"),
    ],
    "SHA-384": [
        (r"(?i)hashlib\.sha384", "HIGH", UsageFunction.HASH, lambda m: None, "ECDAT-SRC-SHA384-001"),
        (r"(?i)MessageDigest\.getInstance\(\"SHA-384\"\)", "HIGH", UsageFunction.HASH, lambda m: None, "ECDAT-SRC-JAVA-SHA384-001"),
        (r"(?i)\bEVP_sha384\b", "HIGH", UsageFunction.HASH, lambda m: None, "ECDAT-SRC-C-SHA384-001"),
    ],
    "SHA-512": [
        (r"(?i)hashlib\.sha512", "HIGH", UsageFunction.HASH, lambda m: None, "ECDAT-SRC-SHA512-001"),
        (r"(?i)MessageDigest\.getInstance\(\"SHA-512\"\)", "HIGH", UsageFunction.HASH, lambda m: None, "ECDAT-SRC-JAVA-SHA512-001"),
        (r"(?i)\bEVP_sha512\b", "HIGH", UsageFunction.HASH, lambda m: None, "ECDAT-SRC-C-SHA512-001"),
    ],
    "SHA-3": [
        (r"(?i)hashlib\.sha3_(224|256|384|512)", "HIGH", UsageFunction.HASH, lambda m: None, "ECDAT-SRC-SHA3-001"),
        (r"(?i)MessageDigest\.getInstance\(\"SHA3-(224|256|384|512)\"\)", "HIGH", UsageFunction.HASH, lambda m: None, "ECDAT-SRC-JAVA-SHA3-001"),
    ],
    "SHA-1": [
        (r"(?i)hashlib\.sha1", "HIGH", UsageFunction.HASH, lambda m: None, "ECDAT-SRC-SHA1-001"),
        (r"(?i)MessageDigest\.getInstance\(\"SHA-1\"\)", "HIGH", UsageFunction.HASH, lambda m: None, "ECDAT-SRC-JAVA-SHA1-001"),
        (r"(?i)createHash\('sha1'\)", "HIGH", UsageFunction.HASH, lambda m: None, "ECDAT-SRC-JS-SHA1-001"),
        (r"(?i)\bEVP_sha1\b", "HIGH", UsageFunction.HASH, lambda m: None, "ECDAT-SRC-C-SHA1-001"),
    ],
    "MD5": [
        (r"(?i)hashlib\.md5", "HIGH", UsageFunction.HASH, lambda m: None, "ECDAT-SRC-MD5-001"),
        (r"(?i)MessageDigest\.getInstance\(\"MD5\"\)", "HIGH", UsageFunction.HASH, lambda m: None, "ECDAT-SRC-JAVA-MD5-001"),
        (r"(?i)createHash\('md5'\)", "HIGH", UsageFunction.HASH, lambda m: None, "ECDAT-SRC-JS-MD5-001"),
        (r"(?i)\bEVP_md5\b", "HIGH", UsageFunction.HASH, lambda m: None, "ECDAT-SRC-C-MD5-001"),
    ],
}

COMPILED_PATTERNS: List[Tuple[str, re.Pattern, str, UsageFunction, any, str]] = []
for algo, p_list in PATTERNS.items():
    for p_tuple in p_list:
        regex_str, conf, usage, keysize_extractor, rule_id = p_tuple
        COMPILED_PATTERNS.append((algo, re.compile(regex_str), conf, usage, keysize_extractor, rule_id))

# High-performance compiled pre-filters for file-level and line-level screening
FILE_CRYPTO_PREFILTER = re.compile(
    r'\b(?:'
    r'rsa|dsa|ecdsa|ecdh|diffiehellman|x25519|ed25519|curve25519|'
    r'aes|des|des3|desede|rc4|arc4|arcfour|chacha20|poly1305|'
    r'sha(?:1|224|256|384|512|3)?|md5|rs(?:256|384|512)|'
    r'hashlib|keypairgenerator|keyagreement|messagedigest|cipher|signature|'
    r'createcipheriv|createhash|createecdh|evp_\w+|rsa_\w+|ssh-rsa|ssh-ed25519|ecdsa-sha2|rsa-sha2|'
    r'secp256\w*|secp384\w*|secp521\w*|prime256\w*|generate_private_key'
    r')\b|aes\d+|evp_|rsa_|secp|prime256|"AES|"DES|"DESede',
    re.IGNORECASE
)

PY_AST_PREFILTER = re.compile(
    r'\b(?:hashlib|rsa|generate_private_key|secp\w*|x25519|ed25519|aes|des|des3|arc4|rc4|chacha20)\b',
    re.IGNORECASE
)

LINE_CRYPTO_PREFILTER = re.compile(
    r'\b(?:rsa|dsa|ecdsa|ecdh|diffiehellman|x25519|ed25519|curve25519|aes|des|des3|desede|rc4|arc4|arcfour|chacha20|poly1305|sha1|sha256|sha384|sha512|sha3|md5|rs(?:256|384|512)|hashlib|keypairgenerator|keyagreement|messagedigest|cipher|signature|createcipheriv|createhash|createecdh|evp_\w+|rsa_\w+|ssh-rsa|ssh-ed25519|ecdsa-sha2|rsa-sha2|secp256|prime256)\b|aes\d+|evp_|rsa_|secp|prime256|"AES|"DES|"DESede',
    re.IGNORECASE
)

def _extract_mode(algo, match) -> str | None:
    if algo != "AES" or not match.groups():
        return None
    gs = list(match.groups())
    mode = None
    if len(gs) >= 1 and gs[0] and re.fullmatch(r"[A-Za-z]+", str(gs[0])):
        mode = str(gs[0]).upper()
    if gs and mode in ("ECB", "CBC", "GCM", "CTR", "CFB", "OFB", "CCM"):
        return mode
    if len(gs) >= 2 and gs[1] and re.fullmatch(r"[A-Za-z]+", str(gs[1])):
        mode = str(gs[1]).upper()
        if mode in ("ECB", "CBC", "GCM", "CTR", "CFB", "OFB", "CCM"):
            return mode
    if gs and mode:
        return mode
    return None


class PythonCryptoASTVisitor(ast.NodeVisitor):
    """AST visitor to detect Python cryptographic API call-sites with high precision."""
    def __init__(self, filepath: str, lines: list):
        self.filepath = filepath
        self.lines = lines
        self.assets = []
        self.matched_lines = set()

    def visit_Call(self, node):
        func_name = ""
        module_name = ""
        full_call = ""
        if isinstance(node.func, ast.Attribute):
            func_name = node.func.attr
            val = node.func.value
            module_name = getattr(val, "id", "") or getattr(val, "attr", "")
            if isinstance(val, ast.Attribute):
                parent_val = getattr(val.value, "id", "")
                full_call = f"{parent_val}.{module_name}.{func_name}" if parent_val else f"{module_name}.{func_name}"
            else:
                full_call = f"{module_name}.{func_name}"
        elif isinstance(node.func, ast.Name):
            func_name = node.func.id
            module_name = ""
            full_call = func_name

        lineno = getattr(node, "lineno", 1)
        line_txt = self.lines[lineno - 1] if 0 < lineno <= len(self.lines) else ""

        # hashlib.md5, hashlib.sha1, hashlib.sha256, hashlib.sha384, hashlib.sha512, sha3
        if module_name == "hashlib" and func_name in ("md5", "sha1", "sha256", "sha384", "sha512", "sha3_224", "sha3_256", "sha3_384", "sha3_512"):
            algo_map = {
                "md5": ("MD5", "ECDAT-SRC-MD5-001"),
                "sha1": ("SHA-1", "ECDAT-SRC-SHA1-001"),
                "sha256": ("SHA-256", "ECDAT-SRC-SHA256-001"),
                "sha384": ("SHA-384", "ECDAT-SRC-SHA384-001"),
                "sha512": ("SHA-512", "ECDAT-SRC-SHA512-001"),
                "sha3_224": ("SHA-3", "ECDAT-SRC-SHA3-001"),
                "sha3_256": ("SHA-3", "ECDAT-SRC-SHA3-001"),
                "sha3_384": ("SHA-3", "ECDAT-SRC-SHA3-001"),
                "sha3_512": ("SHA-3", "ECDAT-SRC-SHA3-001"),
            }
            algo, rule_id = algo_map[func_name]
            self.assets.append(CryptoAsset(
                asset_id=str(uuid.uuid4()),
                asset_type=AssetType.ALGORITHM,
                algorithm=algo,
                primitive=algo,
                key_size=None,
                mode=None,
                padding=None,
                curve=None,
                hash_algo=None,
                library="hashlib",
                file_path=self.filepath,
                line_number=lineno,
                source_snippet=line_txt.strip()[:200],
                confidence="HIGH",
                usage=UsageFunction.HASH,
                rule_id=rule_id,
                provenance="OBSERVED",
                quantum_status=QuantumStatus.SAFE,
                lifetime="L",
                criticality="High",
                exposure="External"
            ))
            self.matched_lines.add(lineno)

        # RSA.generate(bits) or rsa.generate_private_key(...)
        elif (module_name == "RSA" and func_name == "generate") or (func_name == "generate_private_key" and "rsa" in full_call.lower()):
            ksize = 2048
            if node.args and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, int):
                ksize = node.args[0].value
            for kw in node.keywords:
                if kw.arg == "key_size" and isinstance(kw.value, ast.Constant) and isinstance(kw.value.value, int):
                    ksize = kw.value.value

            self.assets.append(CryptoAsset(
                asset_id=str(uuid.uuid4()),
                asset_type=AssetType.ALGORITHM,
                algorithm="RSA",
                primitive="RSA",
                key_size=ksize,
                mode=None,
                padding=None,
                curve=None,
                hash_algo=None,
                library="pycryptodome" if module_name == "RSA" else "cryptography",
                file_path=self.filepath,
                line_number=lineno,
                source_snippet=line_txt.strip()[:200],
                confidence="HIGH",
                usage=UsageFunction.ENCRYPTION,
                rule_id="ECDAT-SRC-RSA-001",
                provenance="OBSERVED",
                quantum_status=QuantumStatus.SAFE,
                lifetime="L",
                criticality="Critical",
                exposure="External"
            ))
            self.matched_lines.add(lineno)

        # ec.generate_private_key(curve)
        elif (func_name == "generate_private_key" and module_name == "ec") or (module_name == "ec" and func_name.startswith("SECP")):
            self.assets.append(CryptoAsset(
                asset_id=str(uuid.uuid4()),
                asset_type=AssetType.ALGORITHM,
                algorithm="ECDSA",
                primitive="ECDSA",
                key_size=256,
                mode=None,
                padding=None,
                curve="SECP256R1",
                hash_algo=None,
                library="cryptography",
                file_path=self.filepath,
                line_number=lineno,
                source_snippet=line_txt.strip()[:200],
                confidence="HIGH",
                usage=UsageFunction.SIGNATURE,
                rule_id="ECDAT-SRC-PY-EC-001",
                provenance="OBSERVED",
                quantum_status=QuantumStatus.SAFE,
                lifetime="L",
                criticality="High",
                exposure="External"
            ))
            self.matched_lines.add(lineno)

        # x25519.X25519PrivateKey.generate()
        elif func_name == "generate" and "x25519" in full_call.lower():
            self.assets.append(CryptoAsset(
                asset_id=str(uuid.uuid4()),
                asset_type=AssetType.ALGORITHM,
                algorithm="X25519",
                primitive="X25519",
                key_size=256,
                mode=None,
                padding=None,
                curve="Curve25519",
                hash_algo=None,
                library="cryptography",
                file_path=self.filepath,
                line_number=lineno,
                source_snippet=line_txt.strip()[:200],
                confidence="HIGH",
                usage=UsageFunction.KEY_EXCHANGE,
                rule_id="ECDAT-SRC-PY-X25519-001",
                provenance="OBSERVED",
                quantum_status=QuantumStatus.SAFE,
                lifetime="L",
                criticality="High",
                exposure="External"
            ))
            self.matched_lines.add(lineno)

        # ed25519.Ed25519PrivateKey.generate()
        elif func_name == "generate" and "ed25519" in full_call.lower():
            self.assets.append(CryptoAsset(
                asset_id=str(uuid.uuid4()),
                asset_type=AssetType.ALGORITHM,
                algorithm="Ed25519",
                primitive="Ed25519",
                key_size=256,
                mode=None,
                padding=None,
                curve="Ed25519",
                hash_algo=None,
                library="cryptography",
                file_path=self.filepath,
                line_number=lineno,
                source_snippet=line_txt.strip()[:200],
                confidence="HIGH",
                usage=UsageFunction.SIGNATURE,
                rule_id="ECDAT-SRC-PY-ED25519-001",
                provenance="OBSERVED",
                quantum_status=QuantumStatus.SAFE,
                lifetime="L",
                criticality="High",
                exposure="External"
            ))
            self.matched_lines.add(lineno)

        # AES.new(key, mode, ...)
        elif module_name == "AES" and func_name == "new":
            mode = None
            if len(node.args) >= 2 and isinstance(node.args[1], ast.Attribute):
                mode = node.args[1].attr.replace("MODE_", "")
            self.assets.append(CryptoAsset(
                asset_id=str(uuid.uuid4()),
                asset_type=AssetType.ALGORITHM,
                algorithm="AES",
                primitive="AES",
                key_size=None,
                mode=mode,
                padding=None,
                curve=None,
                hash_algo=None,
                library="pycryptodome",
                file_path=self.filepath,
                line_number=lineno,
                source_snippet=line_txt.strip()[:200],
                confidence="HIGH",
                usage=UsageFunction.ENCRYPTION,
                rule_id="ECDAT-SRC-AES-001",
                provenance="OBSERVED",
                quantum_status=QuantumStatus.SAFE,
                lifetime="L",
                criticality="High",
                exposure="External"
            ))
            self.matched_lines.add(lineno)

        # DES.new(...)
        elif module_name == "DES" and func_name == "new":
            self.assets.append(CryptoAsset(
                asset_id=str(uuid.uuid4()),
                asset_type=AssetType.ALGORITHM,
                algorithm="DES",
                primitive="DES",
                key_size=56,
                mode="ECB",
                padding=None,
                curve=None,
                hash_algo=None,
                library="pycryptodome",
                file_path=self.filepath,
                line_number=lineno,
                source_snippet=line_txt.strip()[:200],
                confidence="HIGH",
                usage=UsageFunction.ENCRYPTION,
                rule_id="ECDAT-SRC-PY-DES-001",
                provenance="OBSERVED",
                quantum_status=QuantumStatus.SAFE,
                lifetime="L",
                criticality="High",
                exposure="External"
            ))
            self.matched_lines.add(lineno)

        # DES3.new(...)
        elif module_name == "DES3" and func_name == "new":
            self.assets.append(CryptoAsset(
                asset_id=str(uuid.uuid4()),
                asset_type=AssetType.ALGORITHM,
                algorithm="DES3",
                primitive="DES3",
                key_size=112,
                mode=None,
                padding=None,
                curve=None,
                hash_algo=None,
                library="pycryptodome",
                file_path=self.filepath,
                line_number=lineno,
                source_snippet=line_txt.strip()[:200],
                confidence="HIGH",
                usage=UsageFunction.ENCRYPTION,
                rule_id="ECDAT-SRC-DES3-001",
                provenance="OBSERVED",
                quantum_status=QuantumStatus.SAFE,
                lifetime="L",
                criticality="High",
                exposure="External"
            ))
            self.matched_lines.add(lineno)

        # ARC4.new(...)
        elif module_name in ("ARC4", "RC4") and func_name == "new":
            self.assets.append(CryptoAsset(
                asset_id=str(uuid.uuid4()),
                asset_type=AssetType.ALGORITHM,
                algorithm="RC4",
                primitive="RC4",
                key_size=128,
                mode=None,
                padding=None,
                curve=None,
                hash_algo=None,
                library="pycryptodome",
                file_path=self.filepath,
                line_number=lineno,
                source_snippet=line_txt.strip()[:200],
                confidence="HIGH",
                usage=UsageFunction.ENCRYPTION,
                rule_id="ECDAT-SRC-RC4-001",
                provenance="OBSERVED",
                quantum_status=QuantumStatus.SAFE,
                lifetime="L",
                criticality="High",
                exposure="External"
            ))
            self.matched_lines.add(lineno)

        # ChaCha20.new(...) / ChaCha20_Poly1305.new(...)
        elif "chacha20" in module_name.lower() and func_name == "new":
            self.assets.append(CryptoAsset(
                asset_id=str(uuid.uuid4()),
                asset_type=AssetType.ALGORITHM,
                algorithm="ChaCha20",
                primitive="ChaCha20",
                key_size=256,
                mode=None,
                padding=None,
                curve=None,
                hash_algo=None,
                library="pycryptodome",
                file_path=self.filepath,
                line_number=lineno,
                source_snippet=line_txt.strip()[:200],
                confidence="HIGH",
                usage=UsageFunction.ENCRYPTION,
                rule_id="ECDAT-SRC-CHACHA-001",
                provenance="OBSERVED",
                quantum_status=QuantumStatus.SAFE,
                lifetime="L",
                criticality="High",
                exposure="External"
            ))
            self.matched_lines.add(lineno)

        self.generic_visit(node)


def scan_file(filepath: str) -> List[CryptoAsset]:
    # Non-source files (JSON, Markdown, CSV, XML, etc.) must not produce source AST findings
    non_source_exts = ('.json', '.md', '.txt', '.csv', '.xml', '.yml', '.yaml', '.toml', '.lock')
    if filepath.lower().endswith(non_source_exts):
        return []

    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except Exception:
        return []

    # Fast file-level screening: skip files without any crypto keywords
    if not content or not FILE_CRYPTO_PREFILTER.search(content):
        return []

    lines = content.splitlines()
    matched_ast_lines = set()
    ast_succeeded = False
    assets = []

    # Step 1: AST-based Call-Site Analysis for Python source files
    if filepath.endswith('.py') and PY_AST_PREFILTER.search(content):
        try:
            tree = ast.parse(content, filename=filepath)
            visitor = PythonCryptoASTVisitor(filepath, lines)
            visitor.visit(tree)
            assets.extend(visitor.assets)
            matched_ast_lines = visitor.matched_lines
            ast_succeeded = True
        except Exception:
            pass  # Fall back to regex scanning if syntax invalid or dynamic

    # If Python AST parsing succeeded, don't execute raw regex fallback on comments/strings
    if ast_succeeded and filepath.endswith('.py'):
        return assets

    # Step 2: Line-by-line pattern matching (Regex Fallback / Multi-language Java, JS, TS, C)
    for line_idx, line in enumerate(lines):
        line_num = line_idx + 1
        if line_num in matched_ast_lines:
            continue
        line_clean = line.strip()
        if not line_clean:
            continue

        # Skip comment lines to prevent comment text from generating false positives
        if line_clean.startswith(("#", "//", "/*", "*", "<!--", ";", '"""', "'''")):
            continue

        # Skip pure URLs
        if line_clean.startswith(("http://", "https://", "ftp://")):
            continue

        # Fast line-level regex pre-filter
        if not LINE_CRYPTO_PREFILTER.search(line_clean):
            continue

        for algo, compiled_re, conf, usage, keysize_extractor, rule_id in COMPILED_PATTERNS:
            match = compiled_re.search(line_clean)
            if match:
                ksize = None
                try:
                    ksize = keysize_extractor(match)
                except Exception:
                    pass

                asset = CryptoAsset(
                    asset_id=str(uuid.uuid4()),
                    asset_type=AssetType.ALGORITHM,
                    algorithm=algo,
                    primitive=algo,
                    key_size=ksize,
                    mode=_extract_mode(algo, match),
                    padding=None,
                    curve=None,
                    hash_algo=None,
                    library="Unknown",
                    file_path=filepath,
                    line_number=line_num,
                    source_snippet=line_clean[:200],
                    confidence=conf,
                    usage=usage,
                    rule_id=rule_id,
                    provenance="OBSERVED",
                    quantum_status=QuantumStatus.SAFE,
                    lifetime="L",
                    criticality="High",
                    exposure="External"
                )
                assets.append(asset)
                break

    return assets

def run_project_scan(directory: str) -> List[CryptoAsset]:
    results = []
    source_exts = ('.py', '.js', '.java', '.ts', '.jsx', '.tsx', '.c', '.h', '.cpp', '.cc')
    for root, _, files in os.walk(directory):
        # Skip common non-source dirs
        if any(skip in root for skip in ['.git', 'node_modules', 'venv', '__pycache__', '.pytest_cache']):
            continue
        for file in files:
            # Exclude non-source files; specifically exclude JSON fixture files
            if not file.endswith(source_exts):
                continue
            filepath = os.path.join(root, file)
            results.extend(scan_file(filepath))
    return results
