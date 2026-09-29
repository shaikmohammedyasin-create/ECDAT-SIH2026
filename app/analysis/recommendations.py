from app.models.crypto_asset import CryptoAsset, UsageFunction

# Deterministic, explainable recommendation table (source-of-truth §20).
# (detected_primitive, usage) -> dict(primary, alternative, why, hybrid, effort, standard)
RULE = {
    ("RSA", "KEY_EXCHANGE"): dict(
        primary="Hybrid X25519 + ML-KEM-768", alternative="ML-KEM-768",
        why="RSA key exchange is broken by Shor's algorithm (HNDL risk).",
        hybrid="X25519MLKEM768 (TLS hybrids)", effort="Medium — update TLS/servers",
        standard="NIST FIPS 203"),
    ("RSA", "ENCRYPTION"): dict(
        primary="ML-KEM-768 + AES-256 envelope encryption", alternative="AES-256-GCM",
        why="RSA encryption/key-wrapping is broken by Shor's algorithm.",
        hybrid="ML-KEM-768 encapsulate AES-256-GCM data key", effort="Medium",
        standard="NIST FIPS 203"),
    ("ECDH", "KEY_EXCHANGE"): dict(
        primary="Hybrid X25519 + ML-KEM-768", alternative="ML-KEM-768",
        why="ECDH/X25519 key exchange broken by Shor's algorithm (HNDL risk).",
        hybrid="X25519MLKEM768", effort="Low-Medium — update key-agreement paths",
        standard="NIST FIPS 203"),
    ("RSA", "SIGNATURE"): dict(
        primary="ML-DSA-65", alternative="ML-DSA-44",
        why="RSA signatures forgeable once a CRQC exists (TNFL risk).",
        hybrid="RSA + ML-DSA-65 dual signatures", effort="Medium-High — re-issue trust chain",
        standard="NIST FIPS 204"),
    ("ECDSA", "SIGNATURE"): dict(
        primary="ML-DSA-65", alternative="SLH-DSA",
        why="ECDSA signatures broken by Shor's algorithm (TNFL risk).",
        hybrid="ECDSA + ML-DSA-65 dual signatures", effort="Medium — update signers/verifiers",
        standard="NIST FIPS 204"),
    ("DSA", "SIGNATURE"): dict(
        primary="ML-DSA-65", alternative="SLH-DSA",
        why="DSA signatures broken by Shor's algorithm (TNFL risk).",
        hybrid="Dual signing", effort="High — replace DSA entirely", standard="NIST FIPS 204"),
    ("ED25519", "SIGNATURE"): dict(
        primary="ML-DSA-65", alternative="SLH-DSA",
        why="EdDSA signatures broken by Shor's algorithm (TNFL risk).",
        hybrid="Dual signing", effort="Medium", standard="NIST FIPS 204"),
    ("X25519", "KEY_EXCHANGE"): dict(
        primary="Hybrid X25519 + ML-KEM-768", alternative="ML-KEM-768",
        why="X25519 key exchange broken by Shor's algorithm (HNDL risk).",
        hybrid="X25519MLKEM768", effort="Low", standard="NIST FIPS 203"),
    ("AES", "ENCRYPTION"): dict(
        primary="AES-256-GCM", alternative="AES-256-GCM (12-byte IV)",
        why="AES-128 -> ~64-bit quantum security under Grover's algorithm (advisory).",
        hybrid="n/a (symmetric)", effort="Low — rotate to 256-bit keys",
        standard="AES-256-GCM"),
    ("MD5", "HASH"): dict(
        primary="SHA-256 / SHA-384 / SHA-3", alternative="SHA-512",
        why="MD5 is classically broken (collisions) and unsuitable.",
        hybrid="n/a", effort="Low — replace hashing calls + re-hash integrity values",
        standard="FIPS 180-4 / FIPS 202"),
    ("SHA-1", "HASH"): dict(
        primary="SHA-256 / SHA-384 / SHA-3", alternative="SHA-512",
        why="SHA-1 is classically broken (chosen-prefix collisions).",
        hybrid="n/a", effort="Low — replace hashing calls + re-hash integrity values",
        standard="FIPS 180-4 / FIPS 202"),
    ("DES", "ENCRYPTION"): dict(
        primary="AES-256-GCM or ChaCha20-Poly1305", alternative="AES-256-GCM",
        why="DES is classically broken (56-bit key).", hybrid="n/a",
        effort="Low — replace cipher", standard="AES-GCM"),
    ("DES3", "ENCRYPTION"): dict(
        primary="AES-256-GCM or ChaCha20-Poly1305", alternative="AES-256-GCM",
        why="3DES is weak (112-bit, meet-in-the-middle; deprecated).", hybrid="n/a",
        effort="Low — replace cipher", standard="AES-GCM"),
}


def _normalise(algo, usage):
    a = algo.upper()
    if a == "3DES":
        a = "DES3"
    return a, usage


def generate_recommendations(asset: CryptoAsset) -> CryptoAsset:
    """Returns a deterministic PQC/hybrid recommendation based on the rule table."""
    algo, usage = _normalise(asset.algorithm, asset.usage)

    r = RULE.get((algo, usage.name))
    if r is None:
        # Fall back by algorithm for signature vs exchange ambiguity
        if algo in ("RSA", "ECDSA", "DSA", "ED25519"):
            r = RULE.get((algo, "SIGNATURE"))
        if r is None:
            for k, v in RULE.items():
                if k[0] == algo:
                    r = v
                    break

    if r is None:
        asset.recommendation = "Maintain current quantum-safe configuration."
        asset.migration_path = ["No immediate action required."]
        asset.why_risky = "No identified quantum/legacy vulnerability for this primitive."
        asset.migration_effort = "None"
        asset.standard = "n/a"
        return asset

    asset.recommendation = r["primary"]
    asset.hybrid_option = r["hybrid"]
    asset.why_risky = r["why"]
    asset.migration_effort = r["effort"]
    asset.standard = r["standard"]
    if algo in ("RSA", "ECDSA", "DSA", "ED25519") and usage.value != "KEY_EXCHANGE":
        asset.migration_path = [
            f"Phase 1: Enable {r['hybrid']}.",
            f"Phase 2: Migrate to {r['primary']}.",
            "Phase 3: Deprecate classical algorithm.",
        ]
    else:
        asset.migration_path = [
            f"Transition to {r['alternative'] or r['primary']}.",
            f"Enforce {r['primary']}.",
        ]
    return asset
