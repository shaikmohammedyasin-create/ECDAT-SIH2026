package com.enterprise.crypto.tests;

import java.security.KeyPair;
import java.security.KeyPairGenerator;
import java.security.Signature;
import java.security.MessageDigest;
import java.security.KeyFactory;
import javax.crypto.Cipher;
import javax.crypto.KeyAgreement;
import javax.crypto.spec.SecretKeySpec;

public class CryptoSamples {
    public KeyPair testRsaGen() throws Exception {
        KeyPairGenerator kpg = KeyPairGenerator.getInstance("RSA");
        kpg.initialize(2048);
        return kpg.generateKeyPair();
    }

    public KeyPair testDsaGen() throws Exception {
        KeyPairGenerator kpg = KeyPairGenerator.getInstance("DSA");
        kpg.initialize(1024);
        return kpg.generateKeyPair();
    }

    public KeyPair testEcGen() throws Exception {
        KeyPairGenerator kpg = KeyPairGenerator.getInstance("EC");
        return kpg.generateKeyPair();
    }

    public byte[] testAesGcm(byte[] data, byte[] key) throws Exception {
        Cipher c = Cipher.getInstance("AES/GCM/NoPadding");
        c.init(Cipher.ENCRYPT_MODE, new SecretKeySpec(key, "AES"));
        return c.doFinal(data);
    }

    public byte[] testDes(byte[] data, byte[] key) throws Exception {
        Cipher c = Cipher.getInstance("DES/ECB/PKCS5Padding");
        c.init(Cipher.ENCRYPT_MODE, new SecretKeySpec(key, "DES"));
        return c.doFinal(data);
    }

    public byte[] test3Des(byte[] data, byte[] key) throws Exception {
        Cipher c = Cipher.getInstance("DESede/CBC/PKCS5Padding");
        c.init(Cipher.ENCRYPT_MODE, new SecretKeySpec(key, "DESede"));
        return c.doFinal(data);
    }

    public byte[] testRc4(byte[] data, byte[] key) throws Exception {
        Cipher c = Cipher.getInstance("RC4");
        c.init(Cipher.ENCRYPT_MODE, new SecretKeySpec(key, "RC4"));
        return c.doFinal(data);
    }

    public byte[] testSha256(byte[] data) throws Exception {
        return MessageDigest.getInstance("SHA-256").digest(data);
    }

    public byte[] testSha1(byte[] data) throws Exception {
        return MessageDigest.getInstance("SHA-1").digest(data);
    }

    public byte[] testMd5(byte[] data) throws Exception {
        return MessageDigest.getInstance("MD5").digest(data);
    }

    public KeyAgreement testEcdh() throws Exception {
        return KeyAgreement.getInstance("ECDH");
    }
}
