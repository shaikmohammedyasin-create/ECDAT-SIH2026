"""
Controlled Python crypto sample — known planted findings (ground truth).

Planted (expected): RSA-2048, ECDSA P-256, AES-128-CBC, SHA-256, SHA-1, MD5.
"""
import hashlib
import os
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, DES3
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA1
from cryptography.hazmat.primitives.asymmetric import ec


# P1: RSA 2048 key generation (Shor-broken)
def gen_rsa():
    key = RSA.generate(2048)
    return key.publickey().export_key()


# P2: ECDSA P-256 (Shor-broken)
def gen_ec():
    priv = ec.generate_private_key(ec.SECP256R1())
    return priv.public_key()


# P3: AES-128-CBC (Grover-weakened)
def aes_enc(key, iv, data):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return cipher.encrypt(data)


# P4: SHA-256 (quantum-safe)
def h_sha256(data):
    return hashlib.sha256(data).hexdigest()


# P5: SHA-1 (classically broken)
def h_sha1(data):
    return hashlib.sha1(data).hexdigest()


# P6: MD5 (classically broken)
def h_md5(data):
    return hashlib.md5(data).hexdigest()


# P7: 3DES (classically broken)
def des3_enc(key, data):
    return DES3.new(key, DES3.MODE_ECB).encrypt(data)
