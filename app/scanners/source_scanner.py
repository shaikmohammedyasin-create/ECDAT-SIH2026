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
        (r"(?i)KeyPairGenerator\.getInstance\(\"RSA\"\).*?initialize\((\d+)\)", "MEDIUM", UsageFunction.ENCRYPTION, lambda m: int(m.group(1)), "ECDAT-SRC-JAVA-RSA-001"),
        (r"(?i)RS256", "HIGH", UsageFunction.SIGNATURE, lambda m: 2048, "ECDAT-SRC-JS-RSA-001"),
        (r"(?i)RSA", "LOW", UsageFunction.ENCRYPTION, lambda m: None, "ECDAT-SRC-RSA-GEN"),
    ],
    "DSA": [
        (r"(?i)Signature\.getInstance\(\"SHA1withDSA\"\)", "HIGH", UsageFunction.SIGNATURE, lambda m: None, "ECDAT-SRC-JAVA-DSA-001"),
    ],
    "ECDSA": [
        (r"(?i)ECDSA", "MEDIUM", UsageFunction.SIGNATURE, lambda m: None, "ECDAT-SRC-ECDSA-GEN"),
        (r"(?i)SECP256R1|secp256k1", "MEDIUM", UsageFunction.SIGNATURE, lambda m: 256, "ECDAT-SRC-PY-EC-001"),
    ],
    "ECDH": [
        (r"(?i)createECDH\('([^']+)'\)", "HIGH", UsageFunction.KEY_EXCHANGE, lambda m: 256, "ECDAT-SRC-JS-ECDH-001"),
    ],
    # Symmetric
    "AES": [
        (r"(?i)AES\.new\([^,]+,\s*AES\.MODE_([A-Z]+)", "HIGH", UsageFunction.ENCRYPTION, lambda m: None, "ECDAT-SRC-AES-001"),
        (r"(?i)createCipheriv\('aes-(\d+)-([a-z]+)'", "HIGH", UsageFunction.ENCRYPTION, lambda m: int(m.group(1)), "ECDAT-SRC-JS-AES-001"),
        (r"(?i)\"AES/([A-Z]+)/([a-zA-Z]+)\"", "HIGH", UsageFunction.ENCRYPTION, lambda m: None, "ECDAT-SRC-JAVA-AES-001"),
    ],
    "DES3": [
        (r"(?i)DES3\.new", "HIGH", UsageFunction.ENCRYPTION, lambda m: 112, "ECDAT-SRC-DES3-001"),
        (r"(?i)createCipheriv\('des-ede3", "HIGH", UsageFunction.ENCRYPTION, lambda m: 112, "ECDAT-SRC-JS-DES3-001"),
    ],
    "DES": [
        (r"(?i)DES/ECB", "HIGH", UsageFunction.ENCRYPTION, lambda m: 56, "ECDAT-SRC-JAVA-DES-001"),
    ],
    # Hash
    "SHA-256": [
        (r"(?i)hashlib\.sha256", "HIGH", UsageFunction.HASH, lambda m: None, "ECDAT-SRC-SHA256-001"),
    ],
    "SHA-1": [
        (r"(?i)hashlib\.sha1", "HIGH", UsageFunction.HASH, lambda m: None, "ECDAT-SRC-SHA1-001"),
        (r"(?i)MessageDigest\.getInstance\(\"SHA-1\"\)", "HIGH", UsageFunction.HASH, lambda m: None, "ECDAT-SRC-JAVA-SHA1-001"),
    ],
    "MD5": [
        (r"(?i)hashlib\.md5", "HIGH", UsageFunction.HASH, lambda m: None, "ECDAT-SRC-MD5-001"),
        (r"(?i)createHash\('md5'\)", "HIGH", UsageFunction.HASH, lambda m: None, "ECDAT-SRC-JS-MD5-001"),
    ]
}

def _extract_mode(algo, match) -> str | None:
    """Extract an AES cipher mode from the matched pattern groups.

    Patterns:
      AES.new(..., AES.MODE_ECB)                  group(1) = mode (e.g. ECB)
      createCipheriv('aes-256-gcm', ...)          group(2) = mode (e.g. gcm)
      "AES/GCM/NoPadding"                         group(1) = mode (GCM), group(2) = padding
    """
    if algo != "AES" or not match.groups():
        return None
    gs = list(match.groups())
    mode = None
    if len(gs) >= 1 and gs[0] and re.fullmatch(r"[A-Za-z]+", str(gs[0])):
        mode = str(gs[0]).upper()
    # For the "AES/ECB/PKCS5Padding" style, group(1) holds the mode already;
    # for createCipheriv('aes-256-gcm'), group(1) is the key size and group(2) the mode.
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
        if isinstance(node.func, ast.Attribute):
            func_name = node.func.attr
            val = node.func.value
            module_name = getattr(val, "id", "") or getattr(val, "attr", "")
        elif isinstance(node.func, ast.Name):
            func_name = node.func.id
            module_name = ""

        lineno = getattr(node, "lineno", 1)
        line_txt = self.lines[lineno - 1] if 0 < lineno <= len(self.lines) else ""

        # hashlib.md5, hashlib.sha1, hashlib.sha256, hashlib.sha384, hashlib.sha512
        if module_name == "hashlib" and func_name in ("md5", "sha1", "sha256", "sha384", "sha512"):
            algo_map = {
                "md5": ("MD5", "ECDAT-SRC-MD5-001"),
                "sha1": ("SHA-1", "ECDAT-SRC-SHA1-001"),
                "sha256": ("SHA-256", "ECDAT-SRC-SHA256-001"),
                "sha384": ("SHA-384", "ECDAT-SRC-SHA384-001"),
                "sha512": ("SHA-512", "ECDAT-SRC-SHA512-001"),
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

        # RSA.generate(bits)
        elif module_name == "RSA" and func_name == "generate":
            ksize = 2048
            if node.args and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, int):
                ksize = node.args[0].value
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
                library="pycryptodome",
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

        self.generic_visit(node)


def scan_file(filepath: str) -> List[CryptoAsset]:
    assets = []
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except Exception:
        return []

    lines = content.splitlines()
    matched_ast_lines = set()

    # Step 1: AST-based Call-Site Analysis for Python source files
    if filepath.endswith('.py'):
        try:
            tree = ast.parse(content, filename=filepath)
            visitor = PythonCryptoASTVisitor(filepath, lines)
            visitor.visit(tree)
            assets.extend(visitor.assets)
            matched_ast_lines = visitor.matched_lines
        except Exception:
            pass  # Fall back to regex scanning if syntax invalid or dynamic

    # Step 2: Line-by-line pattern matching (Regex Fallback / Multi-language Java, JS, TS)
    for line_idx, line in enumerate(lines):
        line_num = line_idx + 1
        if line_num in matched_ast_lines:
            continue
        line_clean = line.strip()
        if not line_clean:
            continue

        for algo, patterns in PATTERNS.items():
            for p_tuple in patterns:
                regex, conf, usage, keysize_extractor, rule_id = p_tuple
                match = re.search(regex, line_clean)
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
    for root, _, files in os.walk(directory):
        # Skip common non-source dirs
        if any(skip in root for skip in ['.git', 'node_modules', 'venv', '__pycache__', '.pytest_cache']):
            continue
        for file in files:
            # Exclude non-source files; specifically exclude JSON fixture files
            if not file.endswith(('.py', '.js', '.java', '.ts', '.jsx', '.tsx')):
                continue
            filepath = os.path.join(root, file)
            results.extend(scan_file(filepath))
    return results
