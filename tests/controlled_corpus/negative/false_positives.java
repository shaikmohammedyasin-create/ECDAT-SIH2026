package com.enterprise.crypto.negative;

/**
 * Documentation mentions RSA, AES, and SHA-256 for architectural guidelines.
 * No cryptographic libraries or Cipher instances are used here.
 */
public class NegativeSample {
    // RSA is mentioned here but no RSA cryptographic operation occurs.
    // DES and MD5 are legacy algorithms mentioned in comments.
    private String rsaDoc = "RSA public key standard discussion";
    private String aesLabel = "AES encryption discussion";
    private int desRetryCount = 0;
    private String documentationUrl = "https://example.com/rsa";

    public String getInfo() {
        String message = "RSA is an algorithm";
        return message;
    }
}
