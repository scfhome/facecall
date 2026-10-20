"""RSA 加密工具模块

实现 PKCS#1 v1.5 RSA 加密，用于密码加密
"""

import base64
from dataclasses import dataclass

from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA


@dataclass(frozen=True)
class RSAPublicKey:
    """RSA 公钥数据结构"""

    modulus: str
    exponent: str


class RSAEncryptor:
    """RSA 加密器"""

    def __init__(self, public_key: RSAPublicKey):
        self.public_key = public_key
        self._rsa_key = self._build_rsa_key()

    def _build_rsa_key(self) -> RSA.RsaKey:
        """从 modulus 和 exponent 构建 RSA 公钥对象"""
        modulus_int = int.from_bytes(base64.b64decode(self.public_key.modulus), byteorder="big")
        exponent_int = int.from_bytes(base64.b64decode(self.public_key.exponent), byteorder="big")
        return RSA.construct((modulus_int, exponent_int))

    def encrypt(self, plaintext: str) -> str:
        """
        加密明文密码

        Args:
            plaintext: 明文密码

        Returns:
            Base64 编码的密文
        """
        cipher = PKCS1_v1_5.new(self._rsa_key)
        ciphertext_bytes = cipher.encrypt(plaintext.encode("utf-8"))
        return base64.b64encode(ciphertext_bytes).decode("utf-8")
