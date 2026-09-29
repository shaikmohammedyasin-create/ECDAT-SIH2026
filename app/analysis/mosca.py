from app.models.crypto_asset import CryptoAsset, QuantumStatus

# Current Year context (e.g. 2026 based on hackathon environment)
CURRENT_YEAR = 2026

def compute_mosca(asset: CryptoAsset, scenario_year: int = 2035, x_lifetime: float = 10.0, y_migration: float = 3.0) -> CryptoAsset:
    """
    Computes Mosca's Theorem:
    X: Data Lifetime / Trust Lifetime (years)
    Y: Migration Time (years)
    Z: Time until CRQC = (Scenario Year - Current Year)

    Condition: At Risk if X + Y > Z (i.e., Margin < 0)
    Margin = Z - (X + Y)
    """
    # Only run Mosca for Quantum Vulnerable or Grover Weakened assets (Skip for Safe/Legacy)
    if asset.quantum_status not in [QuantumStatus.VULNERABLE, QuantumStatus.WEAKENED]:
        asset.mosca_margin = None
        asset.mosca_at_risk = False
        return asset

    z_horizon = float(scenario_year - CURRENT_YEAR)
    margin = z_horizon - (x_lifetime + y_migration)

    asset.mosca_margin = margin
    asset.mosca_at_risk = margin < 0

    return asset
