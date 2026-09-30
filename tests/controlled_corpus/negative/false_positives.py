"""
Negative / False-Positive Corpus — Python
This document discusses AES, RSA, SHA-256, and MD5 in high-level architectural documentation.
No actual cryptographic operations or library invocations are performed here.
"""

# RSA is mentioned here but no RSA cryptographic operation occurs.
# AES-256 is an excellent standard according to NIST.
# Legacy algorithms like DES and MD5 are mentioned for historical compliance.

rsa_description = "RSA stands for Rivest-Shamir-Adleman"
aes_key_label = "label_for_ui_only"
des_flag = False
sha_digest_string = "sha256_mock_string"

url = "https://example.com/rsa"
api_endpoint = "https://crypto.org/algorithms/aes-256"

def print_security_notes():
    message = "RSA is an algorithm"
    notes = "MD5 has collisions, use SHA-256 instead"
    return message + " - " + notes
