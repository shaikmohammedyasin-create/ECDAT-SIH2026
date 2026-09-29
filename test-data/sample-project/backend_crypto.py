"""
Legacy Payment Gateway Service - Cryptographic Implementation
Contains various cryptographic algorithms and keys for testing discovery.
"""
import hashlib
import os
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_OAEP, DES3
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA1, SHA256, MD5
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

# 1. RSA Key Generation (Vulnerable to Shor's Algorithm - Quantum Critical)
def generate_legacy_rsa_keypair():
    # RSA 2048-bit key generation
    key = RSA.generate(2048)
    private_key = key.export_key()
    public_key = key.publickey().export_key()
    return private_key, public_key

# 2. RSA Signature (Vulnerable to Quantum Shor's Algorithm)
def sign_transaction_data(private_key_pem: bytes, payload: bytes) -> bytes:
    key = RSA.import_key(private_key_pem)
    # Using SHA-1 (Broken classically & quantum)
    h = SHA1.new(payload)
    signature = pkcs1_15.new(key).sign(h)
    return signature

# 3. Elliptic Curve Key Exchange (ECDH / ECDSA - Vulnerable to Shor's Algorithm)
def generate_ecc_keys():
    # SECP256R1 / NIST P-256 curve
    ecc_private_key = ec.generate_private_key(ec.SECP256R1())
    ecc_public_key = ecc_private_key.public_key()
    return ecc_private_key, ecc_public_key

# 4. AES-128 Encryption in CBC Mode (Grover's algorithm reduces effective security to 64-bit)
def encrypt_customer_card_data(key: bytes, plaintext: bytes) -> bytes:
    # AES-128-CBC
    iv = os.urandom(16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    # Padding plaintext to block size
    pad_len = 16 - (len(plaintext) % 16)
    padded = plaintext + bytes([pad_len] * pad_len)
    ciphertext = cipher.encrypt(padded)
    return iv + ciphertext

# 5. Triple DES Encryption (Legacy / Deprecated classically & quantum broken)
def encrypt_legacy_pin(key_24bytes: bytes, pin_data: bytes) -> bytes:
    cipher = DES3.new(key_24bytes, DES3.MODE_ECB)
    pad_len = 8 - (len(pin_data) % 8)
    padded = pin_data + bytes([pad_len] * pad_len)
    return cipher.encrypt(padded)

# 6. Weak Hashing Functions (MD5 and SHA-1)
def hash_user_password_weak(password: str) -> str:
    # Deprecated MD5 usage
    return hashlib.md5(password.encode()).hexdigest()

def compute_checksum_sha1(file_bytes: bytes) -> str:
    # Deprecated SHA1 usage
    return hashlib.sha1(file_bytes).hexdigest()

# 7. Secure Hashing Function (SHA-256 - Quantum Resistant)
def compute_secure_hash(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()
