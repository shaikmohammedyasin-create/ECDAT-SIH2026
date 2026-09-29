package com.enterprise.crypto;

import java.security.KeyPair;
import java.security.KeyPairGenerator;
import java.security.Signature;
import java.security.MessageDigest;
import javax.crypto.Cipher;
import javax.crypto.spec.SecretKeySpec;

public class CryptoSample {
    // P1: RSA 2048 (Shor-broken)
    public KeyPair genRsa() throws Exception {
        KeyPairGenerator kpg = KeyPairGenerator.getInstance("RSA");
        kpg.initialize(2048);
        return kpg.generateKeyPair();
    }

    // P2: DSA signature (Shor-broken)
    public byte[] signDsa(KeyPair kp, byte[] d) throws Exception {
        Signature s = Signature.getInstance("SHA1withDSA");
        s.initSign(kp.getPrivate());
        s.update(d);
        return s.sign();
    }

    // P3: AES-GCM (mode detection)
    public byte[] aesGcm(byte[] pt, byte[] key) throws Exception {
        Cipher c = Cipher.getInstance("AES/GCM/NoPadding");
        c.init(Cipher.ENCRYPT_MODE, new SecretKeySpec(key, "AES"));
        return c.doFinal(pt);
    }

    // P4: SHA-1 (classically broken)
    public byte[] sha1(byte[] in) throws Exception {
        return MessageDigest.getInstance("SHA-1").digest(in);
    }

    // P5: DES-ECB (classically broken)
    public byte[] desEcb(byte[] d, byte[] key) throws Exception {
        Cipher c = Cipher.getInstance("DES/ECB/PKCS5Padding");
        c.init(Cipher.ENCRYPT_MODE, new SecretKeySpec(key, "DES"));
        return c.doFinal(d);
    }
}
