"""
Controlled Ground-Truth: Cryptographic Hashes
Planting: MD5, SHA-1, SHA-256, SHA-384, SHA-512, SHA-3
"""
import hashlib

def hash_md5(data):
    return hashlib.md5(data).hexdigest()

def hash_sha1(data):
    return hashlib.sha1(data).hexdigest()

def hash_sha256(data):
    return hashlib.sha256(data).hexdigest()

def hash_sha384(data):
    return hashlib.sha384(data).hexdigest()

def hash_sha512(data):
    return hashlib.sha512(data).hexdigest()

def hash_sha3(data):
    return hashlib.sha3_256(data).hexdigest()
