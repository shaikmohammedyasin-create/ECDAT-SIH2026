/**
 * Authentication and Token Service
 * Implements JWT authentication, legacy token encryption, and hashing.
 */
const crypto = require('crypto');
const jwt = require('jsonwebtoken');

// 1. RSA Token Signing (Quantum Vulnerable via Shor's Algorithm)
function generateAuthToken(userPayload, privateKeyPem) {
    return jwt.sign(userPayload, privateKeyPem, {
        algorithm: 'RS256',
        expiresIn: '24h'
    });
}

// 2. Legacy Session Encryption with DES-EDE3 (Triple DES)
function encryptSessionCookie(cookieData, secretKey) {
    const iv = crypto.randomBytes(8);
    const cipher = crypto.createCipheriv('des-ede3-cbc', secretKey, iv);
    let encrypted = cipher.update(cookieData, 'utf8', 'hex');
    encrypted += cipher.final('hex');
    return { iv: iv.toString('hex'), data: encrypted };
}

// 3. ECDH Key Agreement (Elliptic Curve Diffie-Hellman - Quantum Vulnerable)
function computeSharedSecret(peerPublicKeyHex) {
    const ecdh = crypto.createECDH('secp256k1');
    ecdh.generateKeys();
    const sharedSecret = ecdh.computeSecret(Buffer.from(peerPublicKeyHex, 'hex'));
    return sharedSecret;
}

// 4. Weak MD5 Hash for API Request Fingerprints
function computeRequestFingerprint(headers) {
    const hash = crypto.createHash('md5');
    hash.update(JSON.stringify(headers));
    return hash.digest('hex');
}

// 5. Modern AES-256-GCM Encryption (Quantum Resistant - 128-bit quantum security)
function encryptSensitiveSecret(secretText, key32Bytes) {
    const iv = crypto.randomBytes(12);
    const cipher = crypto.createCipheriv('aes-256-gcm', key32Bytes, iv);
    let encrypted = cipher.update(secretText, 'utf8', 'hex');
    encrypted += cipher.final('hex');
    const authTag = cipher.getAuthTag().toString('hex');
    return { iv: iv.toString('hex'), tag: authTag, data: encrypted };
}

module.exports = {
    generateAuthToken,
    encryptSessionCookie,
    computeSharedSecret,
    computeRequestFingerprint,
    encryptSensitiveSecret
};
