"""Generate a real self-signed X.509 test certificate for the controlled corpus."""
import datetime
import os
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa

SAFE_1900 = datetime.datetime(2000, 1, 1, 12, 0, 0)
SAFE_FAIR_2030 = datetime.datetime(2030, 6, 1, 12, 0, 0)

def main():
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "IN"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Enterprise Secure Corp"),
        x509.NameAttribute(NameOID.COMMON_NAME, "api.enterprise-secure.internal"),
    ])
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(SAFE_1900)
        .not_valid_after(SAFE_FAIR_2030)
        .add_extension(
            x509.SubjectAlternativeName([x509.DNSName("api.enterprise-secure.internal")]),
            critical=False,
        )
        .sign(key, hashes.SHA256())
    )
    out_dir = os.path.join(os.path.dirname(__file__), "..", "test_corpus", "certificates")
    os.makedirs(out_dir, exist_ok=True)
    cert_path = os.path.join(out_dir, "test_cert.pem")
    with open(cert_path, "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))
    print("Wrote", cert_path)
    print("Subject:", subject.rfc4514_string())
    # NOTE: private key is generated transiently and NOT written to disk (security rule).

if __name__ == "__main__":
    main()
