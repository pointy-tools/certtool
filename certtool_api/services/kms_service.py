from typing import TYPE_CHECKING

import boto3
from attrs import define

if TYPE_CHECKING:
    from mypy_boto3_kms import KMSClient

from certtool_api.core import CertToolError

DEFAULT_KMS_KEY_ALIAS: str = "alias/certtool-private-keys"


@define
class KMSService:
    """
    This class is used to interact with the AWS Key Management Service

    :param key_id: The id of the key to use
    :param profile_name: The name of the AWS profile to use

    :Example:

    >>> from certtool_api.services import KMSService
    >>> kms = KMSService(key_id="alias/certtool-private-keys")
    >>> kms.encrypt("Hello World")
    """

    key_id: str = DEFAULT_KMS_KEY_ALIAS
    profile_name: str | None = None
    encryption_context: dict[str, str] | None = None
    _endpoint_url: str | None = None

    @property
    def _client(self) -> "KMSClient":
        """
        This method is used to get a KMS client

        :return: The KMS client
        """
        return boto3.session.Session(profile_name=self.profile_name).client(
            "kms", endpoint_url=self._endpoint_url
        )

    def encrypt(
        self, data: bytes, encryption_context: dict[str, str] | None = None
    ) -> bytes:
        """
        This method is used to encrypt data using KMS

        :param data: The data to encrypt
        :param encryption_context: The encryption context to use

        :return: The encrypted data
        """
        if not encryption_context:
            encryption_context = self.encryption_context
        params: dict[str, str | bytes | dict] = {
            "KeyId": self.key_id,
            "Plaintext": data,
        }
        if encryption_context:
            params["EncryptionContext"] = encryption_context
        resp: dict = self._client.encrypt(**params)
        return resp["CiphertextBlob"]

    def decrypt(
        self, data: bytes, encryption_context: dict[str, str] | None = None
    ) -> bytes:
        """
        This method is used to decrypt data using KMS

        :param data: The data to decrypt
        :param encryption_context: The encryption context to use

        :return: The decrypted data
        """
        if not encryption_context:
            encryption_context = self.encryption_context
        params: dict[str, str | bytes | dict] = {"CiphertextBlob": data}
        if encryption_context:
            params["EncryptionContext"] = encryption_context
        try:
            resp: dict = self._client.decrypt(**params)
        except self._client.exceptions.InvalidCiphertextException:
            raise KMSServiceError("Invalid ciphertext")
        return resp["Plaintext"]


class KMSServiceError(CertToolError):
    """KMS Service Error"""
