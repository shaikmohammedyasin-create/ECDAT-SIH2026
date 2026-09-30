"""
Controlled Ground-Truth: Elliptic Curve Cryptography
Planting: ECDSA (SECP256R1), ECDSA (secp256k1), X25519, Ed25519
"""
from cryptography.hazmat.primitives.asymmetric import ec, x25519, ed25519

def gen_ecdsa_p256():
    return ec.generate_private_key(ec.SECP256R1())

def gen_ecdsa_k1():
    return ec.generate_private_key(ec.SECP256K1())

def gen_x25519():
    return x25519.X25519PrivateKey.generate()

def gen_ed25519():
    return ed25519.Ed25519PrivateKey.generate()
