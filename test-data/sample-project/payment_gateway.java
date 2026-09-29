package com.enterprise.security.payment;

import javax.crypto.Cipher;
import javax.crypto.KeyGenerator;
import javax.crypto.SecretKey;
import javax.crypto.spec.GCMParameterSpec;
import javax.crypto.spec.SecretKeySpec;
import java.security.KeyPair;
import java.security.KeyPairGenerator;
import java.security.Signature;
import java.security.MessageDigest;
import java.security.Security;
import org.bouncycastle.jce.provider.BouncyCastleProvider;

public class PaymentSecurityManager {

    static {
        Security.addProvider(new BouncyCastleProvider());
    }

    // 1. RSA 2048 KeyPair Generation (Shor's Algorithm - Quantum Critical)
    public KeyPair generateRsaKeyPair() throws Exception {
        KeyPairGenerator kpg = KeyPairGenerator.getInstance("RSA");
        kpg.initialize(2048);
        return kpg.generateKeyPair();
    }

    // 2. DSA Signature (Deprecated & Broken by Shor's Algorithm)
    public byte[] signWithDsa(KeyPair keyPair, byte[] transaction) throws Exception {
        Signature dsa = Signature.getInstance("SHA1withDSA");
        dsa.initSign(keyPair.getPrivate());
        dsa.update(transaction);
        return dsa.sign();
    }

    // 3. AES-GCM 128-bit Encryption (Grover's threat: 64-bit effective quantum security)
    public byte[] encryptPayloadAesGcm(byte[] plaintext, SecretKey key, byte[] iv) throws Exception {
        Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding");
        GCMParameterSpec spec = new GCMParameterSpec(128, iv);
        cipher.init(Cipher.ENCRYPT_MODE, key, spec);
        return cipher.doFinal(plaintext);
    }

    // 4. Legacy DES Encryption in ECB mode (Insecure & Broken)
    public byte[] encryptWithLegacyDes(byte[] data, byte[] keyBytes) throws Exception {
        SecretKeySpec keySpec = new SecretKeySpec(keyBytes, "DES");
        Cipher cipher = Cipher.getInstance("DES/ECB/PKCS5Padding");
        cipher.init(Cipher.ENCRYPT_MODE, keySpec);
        return cipher.doFinal(data);
    }

    // 5. SHA-1 Hashing (Broken)
    public byte[] computeSha1(byte[] input) throws Exception {
        MessageDigest md = MessageDigest.getInstance("SHA-1");
        return md.digest(input);
    }
}
