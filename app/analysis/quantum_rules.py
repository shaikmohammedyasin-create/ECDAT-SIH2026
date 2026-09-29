from app.models.crypto_asset import CryptoAsset, QuantumStatus, QuantumVulnClass, UsageFunction

# Shor-broken public-key systems (source-of-truth §14)
SHOR_BROKEN = {"RSA", "DSA", "ECDSA", "ECDH", "DH", "DHE", "X25519", "ED25519"}

# Classically broken (independent of quantum) — source-of-truth §14
CLASSICALLY_BROKEN = {"MD5", "SHA-1", "SHA1", "DES", "DES3", "3DES", "RC4"}

# Quantum-safe (for this analysis)
QUANTUM_SAFE = {"SHA-256", "SHA-384", "SHA-512", "SHA-3", "AES-256", "ML-KEM", "ML-DSA", "SLH-DSA"}


def seed_classification(asset: CryptoAsset) -> CryptoAsset:
    """Populate source-of-truth unified-schema classification defaults when not set."""
    if asset.data_lifetime_years is None:
        asset.data_lifetime_years = {"S": 3, "M": 10, "L": 20, "VL": 30}.get(asset.lifetime, 10)
    if asset.business_criticality is None:
        asset.business_criticality = {"Critical": 5, "High": 4, "Med": 3, "Medium": 3, "Low": 2}.get(
            asset.criticality, 3)
    if asset.migration_time_years is None:
        asset.migration_time_years = 3.0
    return asset


def apply_quantum_rules(asset: CryptoAsset) -> CryptoAsset:
    """Applies Shor/Grover/legacy logic to determine quantum vulnerability class."""
    algo = asset.algorithm.upper()

    asset = seed_classification(asset)

    # Normalise aliases
    if algo == "3DES":
        algo = "DES3"

    # Legacy broken (classically broken, independent of quantum)
    if algo in CLASSICALLY_BROKEN:
        asset.quantum_status = QuantumStatus.LEGACY_BROKEN
        asset.quantum_vuln_class = QuantumVulnClass.CLASSICALLY_BROKEN
        return asset

    # Asymmetric: Shor-broken
    if algo in SHOR_BROKEN:
        asset.quantum_status = QuantumStatus.VULNERABLE
        asset.quantum_vuln_class = QuantumVulnClass.SHOR_BROKEN

        # HNDL vs TNFL distinction (source-of-truth §15)
        if asset.usage in [UsageFunction.ENCRYPTION, UsageFunction.KEY_EXCHANGE]:
            asset.hndl_risk = True   # Harvest Now, Decrypt Later (confidentiality)
        elif asset.usage == UsageFunction.SIGNATURE:
            asset.tnfl_risk = True   # Trust Now, Forge Later (authenticity)
        elif asset.asset_type.value == "Certificate":
            asset.tnfl_risk = True
        return asset

    # Symmetric: Grover-weakened (advisory priority, NOT equivalent to Shor exposure)
    if algo == "AES":
        if asset.key_size and asset.key_size >= 256:
            asset.quantum_status = QuantumStatus.SAFE
            asset.quantum_vuln_class = QuantumVulnClass.QUANTUM_SAFE
        elif asset.key_size and asset.key_size < 256:
            asset.quantum_status = QuantumStatus.WEAKENED
            asset.quantum_vuln_class = QuantumVulnClass.GROVER_WEAKENED
            asset.why_risky = f"AES-{asset.key_size} is weakened by Grover's algorithm to ~{asset.key_size // 2}-bit effective security."
        else:
            # Key size undetermined: cannot verify 256-bit safe strength. Represent uncertainty explicitly.
            asset.quantum_status = QuantumStatus.WEAKENED
            asset.quantum_vuln_class = QuantumVulnClass.GROVER_WEAKENED
            asset.why_risky = "AES key size undetermined; treated as Grover-weakened (uncertain strength) rather than verified quantum-safe."
        return asset

    # Hash/other known quantum-safe
    if algo in QUANTUM_SAFE or algo.startswith("SHA-"):
        asset.quantum_status = QuantumStatus.SAFE
        asset.quantum_vuln_class = QuantumVulnClass.QUANTUM_SAFE
        return asset

    # Unknown -> leave Safe, low-confidence
    asset.quantum_status = QuantumStatus.SAFE
    asset.quantum_vuln_class = QuantumVulnClass.QUANTUM_SAFE
    return asset
