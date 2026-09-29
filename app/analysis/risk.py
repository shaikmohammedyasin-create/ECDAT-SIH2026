from app.models.crypto_asset import CryptoAsset, QuantumStatus


def calculate_risk_score(asset: CryptoAsset) -> CryptoAsset:
    """
    Transparent 0-100 priority heuristic (source-of-truth §19):

        Priority = 100 × (
            0.35 × QuantumExposure
          + 0.25 × BusinessCriticality
          + 0.15 × ExposureSurface
          + 0.15 × DataSensitivity
          + 0.10 × (1 - CryptoAgility)
        )

    All inputs normalised to [0,1]. Bands: 80-100 Critical, 60-79 High,
    40-59 Medium, 20-39 Low, <20 Info. CLASSICALLY_BROKEN assets receive a
    Hygiene-Critical label.
    """
    # ---- 1. QuantumExposure (0.35) ----
    # SHOR_BROKEN -> 1.0 ; GROVER_WEAKENED -> 0.5 ; CLASSICALLY_BROKEN -> 0.7 ;
    # QUANTUM_SAFE -> 0.0. Mosca at-risk boosts exposure for vulnerable/weakened.
    q = asset.quantum_status
    if q == QuantumStatus.VULNERABLE:
        q_exp = 1.0
    elif q == QuantumStatus.LEGACY_BROKEN:
        q_exp = 0.7
    elif q == QuantumStatus.WEAKENED:
        q_exp = 0.5
    else:
        q_exp = 0.0
    # Mosca at-risk is a strong exposure signal for classically-survivable primitives
    if asset.mosca_at_risk and q in (QuantumStatus.VULNERABLE, QuantumStatus.WEAKENED):
        q_exp = max(q_exp, 0.9)

    # ---- 2. BusinessCriticality (0.25) ----
    crit_map = {"Critical": 1.0, "High": 0.75, "Med": 0.5, "Medium": 0.5, "Low": 0.25}
    c_exp = crit_map.get(asset.criticality, 0.5)

    # ---- 3. ExposureSurface (0.15) ----
    exp_map = {"External": 1.0, "Internal": 0.6, "Air-gapped": 0.3, "Offline": 0.3}
    e_exp = exp_map.get(asset.exposure, 0.6)

    # ---- 4. DataSensitivity (0.15) ----
    # Derived from lifetime/type heuristic for prototype transparency.
    sens_map = {"Archival": 1.0, "VL": 1.0, "L": 0.8, "M": 0.55, "S": 0.3}
    d_exp = sens_map.get(asset.lifetime, 0.55)

    # ---- 5. CryptoAgility (0.10) ----
    # configurable/provider-based > hard-coded/static/embedded. We approximate:
    # certificate/assets -> low agility (0.4) ; source regex -> low (0.3) ; library -> 0.8
    agility = 0.8
    if asset.asset_type.value == "Certificate":
        agility = 0.4
    elif asset.asset_type.value in ("Algorithm", "Protocol"):
        agility = 0.3

    score = 100 * (
        0.35 * q_exp
        + 0.25 * c_exp
        + 0.15 * e_exp
        + 0.15 * d_exp
        + 0.10 * (1 - agility)
    )
    asset.risk_score = round(score, 1)

    if score >= 80:
        asset.risk_band = "Critical"
    elif score >= 60:
        asset.risk_band = "High"
    elif score >= 40:
        asset.risk_band = "Medium"
    elif score >= 20:
        asset.risk_band = "Low"
    else:
        asset.risk_band = "Info"

    # Hygiene-Critical label for classically broken crypto (independent of quantum)
    if q == QuantumStatus.LEGACY_BROKEN:
        asset.risk_band = "Critical"
        asset.hygiene_critical = True

    return asset
