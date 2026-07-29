import os
import struct
import hashlib
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

class AESCTR:
    @staticmethod
    def encrypt(key: bytes, data: bytes, iv: bytes = None) -> tuple:
        if iv is None:
            iv = os.urandom(16)
        cipher = Cipher(algorithms.AES(key), modes.CTR(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        encrypted = encryptor.update(data) + encryptor.finalize()
        return encrypted, iv

    @staticmethod
    def decrypt(key: bytes, data: bytes, iv: bytes) -> bytes:
        cipher = Cipher(algorithms.AES(key), modes.CTR(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        decrypted = decryptor.update(data) + decryptor.finalize()
        return decrypted

class RC4MD5:
    @staticmethod
    def _ksa(key: bytes) -> list:
        s = list(range(256))
        j = 0
        for i in range(256):
            j = (j + s[i] + key[i % len(key)]) % 256
            s[i], s[j] = s[j], s[i]
        return s

    @staticmethod
    def _prga(s: list, length: int) -> bytes:
        i = j = 0
        keystream = bytearray()
        for _ in range(length):
            i = (i + 1) % 256
            j = (j + s[i]) % 256
            s[i], s[j] = s[j], s[i]
            keystream.append(s[(s[i] + s[j]) % 256])
        return bytes(keystream)

    @staticmethod
    def encrypt(key: bytes, data: bytes, iv: bytes = None) -> tuple:
        if iv is None:
            iv = os.urandom(16)
        md5_hash = hashlib.md5()
        md5_hash.update(iv + key)
        rc4_key = md5_hash.digest()
        s = RC4MD5._ksa(rc4_key)
        keystream = RC4MD5._prga(s, len(data))
        encrypted = bytes(a ^ b for a, b in zip(data, keystream))
        return encrypted, iv

    @staticmethod
    def decrypt(key: bytes, data: bytes, iv: bytes) -> bytes:
        return RC4MD5.encrypt(key, data, iv)[0]

class KeyDerivation:
    @staticmethod
    def pbkdf2(password: str, salt: bytes = None, iterations: int = 100000, key_length: int = 32) -> bytes:
        if salt is None:
            salt = os.urandom(16)
        key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, iterations, dklen=key_length)
        return key, salt
