from typing import Protocol

from certtool_api.core import Certificate


class KeyStore(Protocol):
    def save(self, key: bytes) -> str:
        ...

    def get(self, key_ref: str) -> bytes:
        ...


class CertificateSigner(Protocol):
    def issue_certificate(self, certificate: Certificate) -> Certificate:
        ...


class CertificateManager(Protocol):
    def request_certificate(self, certificate: Certificate) -> Certificate:
        ...

    def export_certificate(self, certificate_ref: str) -> Certificate:
        ...


class CertificateStore(Protocol):
    def save(self, certificate: Certificate) -> str:
        ...

    def get(self, certificate_ref: str) -> Certificate:
        ...

    def list(self) -> list[Certificate]:
        ...

    def delete(self, certificate_ref: str) -> None:
        ...

    def find(self, **kwargs) -> list[Certificate]:
        ...
