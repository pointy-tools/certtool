# Filename: private_key.py

from enum import Enum
from hashlib import sha256

from attrs import define
from cryptography.hazmat.backends.openssl.rsa import RSAPrivateKey
from cryptography.hazmat.primitives.asymmetric.rsa import generate_private_key
from cryptography.hazmat.primitives.serialization import (
    BestAvailableEncryption,
    Encoding,
    NoEncryption,
    PrivateFormat,
    load_pem_private_key,
)

from .base import CertToolError


class KeyTypes(Enum):
    """
    This class is used to represent the different types of keys

    We currently only support RSA keys, when we add support for others
    they go here
    """

    RSA = "RSA"


@define
class PrivateKey:
    """
    This class is used to represent a private key

    :param key: The private key
    :param algorithm: The algorithm used to generate the key
    """

    key: RSAPrivateKey | None = None
    public_exponent: int = 65537
    key_size: int = 4096
    key_type: KeyTypes = KeyTypes.RSA
    _kms_encrypted_key: bytes | None = None
    _kms_encryption_context: dict[str, str] | None = None

    # property returning the fingerprint of the public key portion of self.key
    @property
    def fingerprint(self) -> str:
        if not self.key:
            raise PrivateKeyError("Key not set.")
        return sha256(
            self.key.public_key().public_numbers().n.to_bytes(512, "big")
        ).hexdigest()

    # function to generate a pem bytes string from self.key that raises KeyNotSetError if self.key is None
    @property
    def pem(self) -> bytes:
        if not self.key:
            raise PrivateKeyError("Key not set.")
        return self.get_pem()

    # function to set self.key from a pem bytes string
    @pem.setter
    def pem(self, key_pem: bytes) -> None:
        try:
            self.set_pem(key_pem=key_pem)
        except TypeError as exc:
            if exc.args[0] == "Password was not given but private key is encrypted":
                raise PrivateKeyError(
                    "PEM key provided is encrypted, you must use set_key_pem with a passphrase"
                ) from exc

    def set_pem(self, key_pem: bytes, passphrase: bytes | None = None) -> None:
        """Use this function when your key_pem is encrypted with a passphrase."""
        self.key = load_pem_private_key(data=key_pem, password=passphrase)

    def get_pem(self, passphrase: bytes | None = None) -> bytes:
        """Use this function when your key_pem is encrypted with a passphrase."""
        if passphrase:
            encryption_algorithm = BestAvailableEncryption(passphrase.encode())
        else:
            encryption_algorithm = NoEncryption()
        return self.key.private_bytes(
            encoding=Encoding.PEM,
            format=PrivateFormat.PKCS8,
            encryption_algorithm=encryption_algorithm,
        )

    # class method to create a new PrivateKey instance and generate a new key for it returning the PrivateKey instance
    @classmethod
    def new(
        cls, key_size: int | None = None, public_exponent: int | None = None
    ) -> "PrivateKey":
        key: PrivateKey = cls()
        key.generate_key(key_size=key_size, public_exponent=public_exponent)
        return key

    # method to generate a new RSAPrivateKey and assign it to self.key. It can optionally take key_size and public_exponent arguments or use the defaults from the class. Returns self.
    def generate_key(
        self, key_size: int | None = None, public_exponent: int | None = None
    ) -> "PrivateKey":
        if self.key:
            raise PrivateKeyError("Key already set.")
        if not key_size:
            key_size = self.key_size
        if not public_exponent:
            public_exponent = self.public_exponent
        self.key = generate_private_key(
            public_exponent=public_exponent, key_size=key_size
        )
        return self

    @classmethod
    def from_pem(cls, key_pem: bytes, passphrase: bytes | None = None) -> "PrivateKey":
        """Use this function when your key_pem is encrypted with a passphrase."""
        key: PrivateKey = cls()
        key.set_pem(key_pem=key_pem, passphrase=passphrase)
        return key

    # method to return self.key as a der encoded bytes string
    def get_key_der(self) -> bytes:
        return self.key.private_bytes(Encoding.DER, PrivateFormat.PKCS8, NoEncryption())


class PrivateKeyError(CertToolError):
    """PrivateKey error"""
