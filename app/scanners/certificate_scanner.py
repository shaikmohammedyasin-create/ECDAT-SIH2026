import os
import uuid
from typing import List
from app.models.crypto_asset import CryptoAsset, AssetType, UsageFunction, QuantumStatus

try:
    from cryptography import x509
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives.asymmetric import rsa, dsa, ec, ed25519, x25519
    from cryptography.hazmat.primitives.serialization import pkcs12, load_ssh_public_key
except ImportError:
    x509 = None


def _extract_pubkey_info(public_key) -> tuple[str, int | None]:
    if isinstance(public_key, rsa.RSAPublicKey):
        return "RSA", public_key.key_size
    elif isinstance(public_key, ec.EllipticCurvePublicKey):
        return "ECDSA", public_key.key_size
    elif isinstance(public_key, dsa.DSAPublicKey):
        return "DSA", public_key.key_size
    elif isinstance(public_key, ed25519.Ed25519PublicKey):
        return "Ed25519", 256
    elif isinstance(public_key, x25519.X25519PublicKey):
        return "X25519", 256
    return "Unknown", None


def scan_certificate_file(filepath: str) -> List[CryptoAsset]:
    """Scan certificate and key files (PEM, DER, PKCS#12, SSH pub) without persisting private keys."""
    assets = []
    if not x509:
        return assets

    try:
        with open(filepath, 'rb') as f:
            data = f.read()
    except Exception:
        return []

    ext = os.path.splitext(filepath)[1].lower()

    # --- 1. PKCS#12 (.p12, .pfx) ---
    if ext in ('.p12', '.pfx'):
        try:
            # Try with empty password and None password (standard keystores)
            p12_obj = None
            for pwd in [None, b"", b"changeit"]:
                try:
                    p12_obj = pkcs12.load_key_and_certificates(data, pwd, default_backend())
                    break
                except Exception:
                    continue
            if p12_obj and p12_obj[1]:
                cert = p12_obj[1]
                algo_name, key_size = _extract_pubkey_info(cert.public_key())
                issuer = cert.issuer.rfc4514_string()
                subject = cert.subject.rfc4514_string()
                valid_to = cert.not_valid_after_utc.strftime('%Y-%m-%d')
                assets.append(CryptoAsset(
                    asset_id=str(uuid.uuid4()),
                    asset_type=AssetType.CERTIFICATE,
                    algorithm=algo_name,
                    primitive=algo_name,
                    key_size=key_size,
                    mode=None,
                    padding=None,
                    curve=None,
                    hash_algo=cert.signature_hash_algorithm.name if cert.signature_hash_algorithm else None,
                    library="PKCS#12",
                    file_path=filepath,
                    line_number=1,
                    source_snippet=f"Format: PKCS#12 | Subject: {subject} | Issuer: {issuer} | Valid: {valid_to}",
                    confidence="HIGH",
                    usage=UsageFunction.SIGNATURE,
                    rule_id=f"ECDAT-CERT-P12-001",
                    provenance="OBSERVED",
                    quantum_status=QuantumStatus.VULNERABLE if algo_name in ["RSA", "ECDSA", "DSA"] else QuantumStatus.SAFE,
                    lifetime="L",
                    criticality="Critical",
                    exposure="External"
                ))
                return assets
        except Exception:
            pass

    # --- 2. SSH Public Key (.pub or ssh- prefix) ---
    if ext == '.pub' or data.startswith((b"ssh-rsa", b"ssh-ed25519", b"ecdsa-sha2-")):
        try:
            pub_key = load_ssh_public_key(data, default_backend())
            algo_name, key_size = _extract_pubkey_info(pub_key)
            snippet = data.decode('utf-8', errors='ignore').splitlines()[0][:120] if data else "SSH Public Key"
            assets.append(CryptoAsset(
                asset_id=str(uuid.uuid4()),
                asset_type=AssetType.KEY,
                algorithm=algo_name,
                primitive=algo_name,
                key_size=key_size,
                mode=None,
                padding=None,
                curve=None,
                hash_algo=None,
                library="OpenSSH",
                file_path=filepath,
                line_number=1,
                source_snippet=f"Format: SSH-Public-Key | KeySize: {key_size} | {snippet}",
                confidence="HIGH",
                usage=UsageFunction.SIGNATURE,
                rule_id=f"ECDAT-CERT-SSH-001",
                provenance="OBSERVED",
                quantum_status=QuantumStatus.VULNERABLE if algo_name in ["RSA", "ECDSA", "DSA"] else QuantumStatus.SAFE,
                lifetime="L",
                criticality="High",
                exposure="External"
            ))
            return assets
        except Exception:
            pass

    # --- 3. X.509 Certificate (PEM or DER) ---
    cert = None
    cert_fmt = "PEM"
    try:
        cert = x509.load_pem_x509_certificate(data, default_backend())
    except Exception:
        try:
            cert = x509.load_der_x509_certificate(data, default_backend())
            cert_fmt = "DER"
        except Exception:
            return []

    try:
        algo_name, key_size = _extract_pubkey_info(cert.public_key())
        issuer = cert.issuer.rfc4514_string()
        subject = cert.subject.rfc4514_string()
        valid_to = cert.not_valid_after_utc.strftime('%Y-%m-%d')

        asset = CryptoAsset(
            asset_id=str(uuid.uuid4()),
            asset_type=AssetType.CERTIFICATE,
            algorithm=algo_name,
            primitive=algo_name,
            key_size=key_size,
            mode=None,
            padding=None,
            curve=None,
            hash_algo=cert.signature_hash_algorithm.name if cert.signature_hash_algorithm else None,
            library=f"X.509 {cert_fmt}",
            file_path=filepath,
            line_number=1,
            source_snippet=f"Format: {cert_fmt} | Subject: {subject} | Issuer: {issuer} | Valid Until: {valid_to}",
            confidence="HIGH",
            usage=UsageFunction.SIGNATURE,
            rule_id=f"ECDAT-CERT-{cert_fmt}-001",
            provenance="OBSERVED",
            quantum_status=QuantumStatus.VULNERABLE if algo_name in ["RSA", "ECDSA", "DSA"] else QuantumStatus.SAFE,
            lifetime="L",
            criticality="Critical",
            exposure="External"
        )
        assets.append(asset)
    except Exception:
        pass

    return assets
