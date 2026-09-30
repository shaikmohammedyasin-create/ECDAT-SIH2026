"""
Controlled Ground-Truth: Symmetric Cryptography
Planting: AES-128, AES-256, DES, 3DES, RC4, ChaCha20, ChaCha20-Poly1305
"""
from Crypto.Cipher import AES, DES, DES3, ARC4, ChaCha20, ChaCha20_Poly1305

def use_aes_128(key, iv, data):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return cipher.encrypt(data)

def use_aes_256(key, nonce, data):
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    return cipher.encrypt(data)

def use_des(key, data):
    cipher = DES.new(key, DES.MODE_ECB)
    return cipher.encrypt(data)

def use_3des(key, data):
    cipher = DES3.new(key, DES3.MODE_CBC)
    return cipher.encrypt(data)

def use_rc4(key, data):
    cipher = ARC4.new(key)
    return cipher.encrypt(data)

def use_chacha20(key, nonce, data):
    cipher = ChaCha20.new(key=key, nonce=nonce)
    return cipher.encrypt(data)

def use_chacha20_poly1305(key, nonce, data):
    cipher = ChaCha20_Poly1305.new(key=key, nonce=nonce)
    return cipher.encrypt(data)
