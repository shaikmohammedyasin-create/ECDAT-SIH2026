"""
CycloneDX 1.6 CBOM generator and validator.

Generates a valid CycloneDX 1.6 BOM where every crypto finding becomes a
`cryptographic-asset` component with cryptoProperties, evidence occurrences and
ECDAT-namespaced properties. Crypto libraries are exported as standard `library`
components (CycloneDX 1.6 has no 'library' crypto assetType, so libraries stay
regular components and reference their crypto via dependencies).

Validation is performed with `jsonschema` against the official CycloneDX 1.6
JSON schema bundled in `schemas/bom-1.6.schema.json`.
"""
import json
import os
import uuid
import datetime
from typing import List

from app.models.crypto_asset import CryptoAsset, AssetType

# Internal primitive -> CycloneDX 1.6 cryptoProperties.primitive enum
PRIMITIVE_MAP = {
    "RSA": "pke",
    "DSA": "signature",
    "ECDSA": "signature",
    "ECDH": "key-agree",
    "DH": "key-agree",
    "X25519": "key-agree",
    "ED25519": "signature",
    "AES": "block-cipher",
    "DES": "block-cipher",
    "DES3": "block-cipher",
    "RC4": "stream-cipher",
    "SHA-256": "hash",
    "SHA-384": "hash",
    "SHA-512": "hash",
    "SHA-1": "hash",
    "SHA1": "hash",
    "MD5": "hash",
    "TLS": "key-agree",
    "DH": "key-agree",
    "BCRYPT": "hash",
    "ARGON2": "kdf",
}

# Internal asset type -> CycloneDX component type
ASSET_TO_COMPONENT = {
    "Algorithm": "cryptographic-asset",
    "Certificate": "cryptographic-asset",
    "Protocol": "cryptographic-asset",
    "Key": "related-crypto-material",
    "Library": "library",  # exported as standard component
}

# quantum status -> nistQuantumSecurityLevel (0-5, source-of-truth model)
def _quantum_level(asset: CryptoAsset) -> int:
    cls = asset.quantum_vuln_class.value
    if cls == "SHOR_BROKEN":
        return 0
    if cls == "GROVER_WEAKENED":
        return 1
    if cls == "QUANTUM_SAFE":
        return 3  # AES-256 / hashes assumed Category 3+; ML-KEM => 3
    if cls == "CLASSICALLY_BROKEN":
        return 0
    return 0


def _cx_primitive(asset: CryptoAsset) -> str:
    p = asset.primitive.upper()
    return PRIMITIVE_MAP.get(p, "other")


def _cx_asset_type(asset: CryptoAsset) -> str:
    t = asset.asset_type.value
    if t == "Library":
        return None
    if t == "Key":
        return "related-crypto-material"
    return "algorithm" if t == "Algorithm" else t.lower()


def _ecdat_props(asset: CryptoAsset) -> list:
    props = [
        {"name": "ecdat:quantum-status", "value": asset.quantum_status.value},
        {"name": "ecdat:quantum-class", "value": asset.quantum_vuln_class.value},
        {"name": "ecdat:risk-score", "value": str(asset.risk_score)},
        {"name": "ecdat:risk-band", "value": asset.risk_band},
        {"name": "ecdat:confidence", "value": asset.confidence},
    ]
    if asset.mosca_margin is not None:
        props.append({"name": "ecdat:mosca-margin-years", "value": str(round(asset.mosca_margin, 2))})
        props.append({"name": "ecdat:mosca-at-risk", "value": str(asset.mosca_at_risk).lower()})
    if asset.recommendation:
        props.append({"name": "ecdat:recommendation", "value": asset.recommendation})
    if asset.why_risky:
        props.append({"name": "ecdat:why", "value": asset.why_risky})
    if asset.migration_effort:
        props.append({"name": "ecdat:effort", "value": asset.migration_effort})
    return props


# CycloneDX 1.6 mode enum
VALID_MODES = {"cbc", "ecb", "ccm", "gcm", "cfb", "ofb", "ctr", "other", "unknown"}

# map common java mode/padding strings to valid CycloneDX mode enum values
MODE_ALIAS = {
    "none": "unknown",
    "nopadding": "unknown",
    "nocipherfeedback": "cfb",
}


def _normalise_mode(mode):
    if not mode:
        return None
    m = mode.strip().lower()
    m = MODE_ALIAS.get(m, m)
    return m if m in VALID_MODES else "other"


def _crypto_properties(asset: CryptoAsset) -> dict:
    """Build cryptoProperties for a cryptographic-asset component."""
    props = {"assetType": _cx_asset_type(asset)}
    algo_props = {}
    if asset.primitive:
        algo_props["primitive"] = _cx_primitive(asset)
    if asset.key_size is not None or str(asset.key_size):
        algo_props["parameterSetIdentifier"] = str(asset.key_size) if asset.key_size else "unknown"
    mode = _normalise_mode(asset.mode)
    if mode:
        algo_props["mode"] = mode
    if asset.padding:
        algo_props["padding"] = asset.padding
    if asset.curve:
        algo_props["curve"] = asset.curve
    algo_props["classicalSecurityLevel"] = 112 if asset.key_size and asset.key_size < 3072 else 128
    algo_props["nistQuantumSecurityLevel"] = _quantum_level(asset)
    props["algorithmProperties"] = algo_props
    return props


def _evidence(asset: CryptoAsset) -> dict:
    return {
        "occurrences": [
            {
                "location": asset.file_path,
                "line": asset.line_number,
                "additionalContext": asset.source_snippet[:500],
            }
        ]
    }


def _component(asset: CryptoAsset) -> dict:
    if asset.asset_type.value == "Library":
        # Standard library component (CycloneDX 1.6 has no library crypto assetType)
        comp = {
            "type": "library",
            "bom-ref": asset.cbom_ref or f"lib/{asset.algorithm.lower()}/{asset.library or 'unknown'}",
            "name": asset.library or asset.algorithm,
            "version": asset.library_version or "1.0",
        }
        if asset.recommendation:
            comp["properties"] = [
                {"name": "ecdat:quantum-status", "value": asset.quantum_status.value},
                {"name": "ecdat:recommendation", "value": asset.recommendation},
            ]
        return comp

    comp = {
        "type": "cryptographic-asset",
        "name": f"{asset.algorithm}{'-' + str(asset.key_size) if asset.key_size else ''}",
        "bom-ref": asset.cbom_ref or f"crypto/{asset.asset_type.value.lower()}/{asset.algorithm.lower()}",
        "cryptoProperties": _crypto_properties(asset),
        "evidence": _evidence(asset),
        "properties": _ecdat_props(asset),
    }
    if asset.hndl_risk:
        comp["properties"].append({"name": "ecdat:threat", "value": "HNDL"})
    if asset.tnfl_risk:
        comp["properties"].append({"name": "ecdat:threat", "value": "TNFL"})
    return comp


def generate_cyclonedx_cbom(assets: List[CryptoAsset]) -> dict:
    components = [_component(a) for a in assets]
    cbom = {
        "bomFormat": "CycloneDX",
        "specVersion": "1.6",
        "serialNumber": f"urn:uuid:{uuid.uuid4()}",
        "version": 1,
        "metadata": {
            "timestamp": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "component": {
                "type": "application",
                "name": "Scanned Target Project",
            }
        },
        "components": components,
    }
    return cbom


def validate_cbom(cbom: dict, schema_path: str = None) -> dict:
    """
    Validate a CBOM dict against the official CycloneDX 1.6 JSON schema.
    Returns {"valid": bool, "errors": [...], "schema": path}.
    """
    import jsonschema
    if schema_path is None:
        base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        schema_path = os.path.join(base, "schemas", "bom-1.6.schema.json")
    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)
    validator = jsonschema.Draft7Validator(schema)
    errors = sorted(validator.iter_errors(cbom), key=lambda e: list(e.path))
    if not errors:
        return {"valid": True, "errors": [], "schema": schema_path}
    return {
        "valid": False,
        "errors": [f"{'/'.join(str(p) for p in e.path) or '<root>'}: {e.message}" for e in errors],
        "schema": schema_path,
    }
