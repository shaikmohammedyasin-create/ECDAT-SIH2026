"""
Controlled Ground-Truth: RSA Key Generation with multiple key sizes
Planting: RSA-1024, RSA-2048, RSA-3072, RSA-4096
"""
from Crypto.PublicKey import RSA

def gen_rsa_1024():
    return RSA.generate(1024)

def gen_rsa_2048():
    return RSA.generate(2048)

def gen_rsa_3072():
    return RSA.generate(3072)

def gen_rsa_4096():
    return RSA.generate(4096)
