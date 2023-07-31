from datetime import datetime
from enum import Enum

from attrs import define, field
from cryptography.hazmat.primitives.hashes import SHA256, HashAlgorithm
from cryptography.hazmat.primitives.serialization import Encoding
from cryptography.x509 import Certificate as X509Certificate
from cryptography.x509 import (
    CertificateSigningRequest,
    CertificateSigningRequestBuilder,
    DNSName,
    ExtensionNotFound,
    ExtensionOID,
    Name,
    NameAttribute,
    NameOID,
    ObjectIdentifier,
    SubjectAlternativeName,
    load_pem_x509_certificate,
    load_pem_x509_csr,
)

from .base import CertToolError
from .private_key import PrivateKey
from .subject import Subject
from .tags import Tags

END_CERTIFICATE = b"-----END CERTIFICATE-----\n"


class Status(Enum):
    """
    Status enum class.

    Attributes:
        ACTIVE: The certificate is active.
        INACTIVE: The certificate is inactive.
        EXPIRED: The certificate is expired.
        REVOKED: The certificate is revoked.

    """

    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    EXPIRED = "EXPIRED"
    REVOKED = "REVOKED"

    @classmethod
    def choices(cls) -> list[tuple[str, str]]:
        """
        Return a list of tuples of the enum choices.
        """
        return [(choice.name, choice.value) for choice in cls]


@define
class Certificate:
    """
    Certificate entity class.

    Attributes:
        certificate_id: The certificate ID.
        acm_arn: The ARN of the ACM certificate.
        pa_arn: The ARN of the PA certificate.
        ca_arn: The ARN of the CA certificate.
        certificate: The certificate.
        certificate_pem: The certificate PEM.
        chain: The certificate chain.
        chain_pem: The certificate chain PEM.
        csr: The certificate signing request.
        csr_pem: The certificate signing request PEM.
        key: The private key.
        key_pem: The private key PEM.
        common_name: The common name.
        subject_details: The subject details.
        alternate_names: The alternate names.
        not_before: The not before date.
        not_after: The not after date.
        public_exponent: The public exponent.
        key_size: The key size.
        tags: The tags. see :class:`Tags`
        status: The status. Either ACTIVE, INACTIVE, EXPIRED, or REVOKED.

    """

    certificate_id: int | None = None
    acm_arn: str | None = None
    private_ca_arn: str | None = None
    issuer_ca_arn: str | None = None
    certificate: X509Certificate | None = None
    chain: list[X509Certificate] = field(factory=list)
    csr: CertificateSigningRequest | None = None
    key: PrivateKey | None = None
    alternate_names: list[str] = field(factory=list)
    not_before: datetime | None = None
    not_after: datetime | None = None
    subject: Subject = Subject()
    key_reference: str | None = None
    tags: Tags | None = None
    status: Status | None = None

    # method to return the common_name from self.subject
    @property
    def common_name(self) -> str | None:
        return self.subject.common_name

    # method to set the common_name in self.subject
    @common_name.setter
    def common_name(self, common_name: str) -> None:
        self.subject.common_name = common_name

    # method to return key_pem from the PrivateKey object in self.key
    @property
    def key_pem(self) -> bytes:
        if not self.key:
            raise CertificateError("Key not set.")
        return self.key.pem

    # method to set self.key from a pem bytes string
    @key_pem.setter
    def key_pem(self, key_pem: bytes) -> None:
        if self.key:
            raise CertificateError("Key already set.")
        self.key = PrivateKey.from_pem(key_pem)

    def generate_key(self) -> "Certificate":
        if self.key:
            raise CertificateError("Key already set.")
        self.key = PrivateKey.new()
        return self

    # function to generate a pem bytes string from self.csr that raises CsrNotSetError if self.csr is None
    @property
    def csr_pem(self) -> bytes:
        if not self.csr:
            raise CertificateError("CSR not set.")
        return self.csr.public_bytes(Encoding.PEM)

    # function to set self.csr from a pem bytes string
    @csr_pem.setter
    def csr_pem(self, csr_pem: bytes) -> None:
        self.csr = load_pem_x509_csr(csr_pem)

    # function to generate a pem bytes string from self.certificate that raises CertNotSetError if self.cert is None
    @property
    def certificate_pem(self) -> bytes:
        if not self.certificate:
            raise CertificateError("Certificate not set.")
        return self.certificate.public_bytes(Encoding.PEM)

    # function to set self.certificate from a pem bytes string
    @certificate_pem.setter
    def certificate_pem(self, certificate_pem: bytes) -> None:
        self.certificate = load_pem_x509_certificate(certificate_pem)

    # function to pem bytes string from self.chain that raises CertificateError if self.chain is None
    @property
    def chain_pem(self) -> bytes:
        if not self.chain:
            raise CertificateError("Chain not set.")
        return b"".join(
            [
                cert.public_bytes(Encoding.PEM)
                for cert in self.chain
                if isinstance(cert, X509Certificate)
            ]
        )

    # function to set self.chain from a list of certificates encoded in a single pem bytes string
    @chain_pem.setter
    def chain_pem(self, chain_pem: bytes) -> None:
        self.chain = [
            load_pem_x509_certificate(cert + END_CERTIFICATE)
            for cert in chain_pem.split(END_CERTIFICATE)
            if cert
        ]

    # function to generate a bytes string fingerprint from self.certificate using a default of sha256 that raises CertNotSetError if self.certificate is None
    @property
    def fingerprint(self, hash: HashAlgorithm = SHA256) -> bytes:
        if not self.certificate:
            raise CertificateError("Certificate not set.")
        return self.certificate.fingerprint(hash())

    # function to read self.certificate and use its data to populate self.common_name, self.alternate_names, self.not_before, self.not_after and self.subject assuming self.alternate_names may not be found
    def attrs_from_x509_certificate(self) -> None:
        """
        Read self.certificate and use its data to populate self.common_name, self.alternate_names, self.not_before, self.not_after and self.subject assuming self.alternate_names may not be found

        :return: None

        :raises CertificateError: if self.certificate is None
        """
        if not self.certificate:
            raise CertificateError("Certificate not set.")
        self.subject = self._get_subject_details(self.certificate.subject)
        self.not_before = self.certificate.not_valid_before
        self.not_after = self.certificate.not_valid_after
        try:
            self.alternate_names = self.certificate.extensions.get_extension_for_oid(
                ExtensionOID.SUBJECT_ALTERNATIVE_NAME
            ).value.get_values_for_type(DNSName)
        except ExtensionNotFound:
            pass

    # private function to take a X509Certificate.subject and return a SubjectDetails object checking for missing attributes
    def _get_subject_details(self, subject: Name) -> Subject:
        def _getter(oid: ObjectIdentifier) -> str | None:
            attributes: list[NameAttribute] = subject.get_attributes_for_oid(oid)
            return attributes[0].value if attributes else None

        return Subject(
            country=_getter(NameOID.COUNTRY_NAME),
            state=_getter(NameOID.STATE_OR_PROVINCE_NAME),
            locality=_getter(NameOID.LOCALITY_NAME),
            organization=_getter(NameOID.ORGANIZATION_NAME),
            organizational_unit=_getter(NameOID.ORGANIZATIONAL_UNIT_NAME),
        )

    # method to generate a Certificate. It should take a pem bytes string, parse it, add it to a Certificate and read its attributes into the Certificate. Returns that Certificate.
    @classmethod
    def from_pem(cls, pem: bytes) -> "Certificate":
        certificate = cls()
        certificate.certificate_pem = pem
        certificate.attrs_from_x509_certificate()
        return certificate

    # method with type annotations on all internal variables to generate a new CSR and assign it to self.csr. It can optionally take a list of alternate_names, a RSAPrivateKey, a SubjectDetails object or uses the defaults from the class. The SubjectDetails should be checked for values and only included in the name if not None. Returns self.
    def generate_csr(
        self,
        alternate_names: list[str] | None = None,
        key: PrivateKey | None = None,
        subject: Subject | None = None,
    ) -> "Certificate":
        if not key:
            key = self.key
        if not subject:
            subject = self.subject
        if not alternate_names:
            alternate_names = self.alternate_names
        csr_builder: CertificateSigningRequestBuilder = (
            CertificateSigningRequestBuilder()
        )
        csr_builder = csr_builder.subject_name(subject.to_x509_name())
        if alternate_names:
            csr_builder = csr_builder.add_extension(
                SubjectAlternativeName([DNSName(name) for name in alternate_names]),
                critical=False,
            )
        self.csr = csr_builder.sign(key.key, SHA256())
        return self

    # method to return self.certificate as a der encoded bytes string
    def get_certificate_der(self) -> bytes:
        return self.certificate.public_bytes(Encoding.DER)

    # method to return self.certificate as a pem encoded bytes string
    def get_certificate_pem(self) -> bytes:
        return self.certificate.public_bytes(Encoding.PEM)

    # method to return self.csr as a der encoded bytes string
    def get_csr_der(self) -> bytes:
        return self.csr.public_bytes(Encoding.DER)

    # method to return self.csr as a pem encoded bytes string
    def get_csr_pem(self) -> bytes:
        return self.csr.public_bytes(Encoding.PEM)

    # method to return self.key as a der encoded bytes string
    def get_key_der(self) -> bytes:
        return self.key.get_key_der()

    def get_pem_safe(self, pem: str) -> str:
        if getattr(self, pem):
            return getattr(self, f"{pem}_pem").decode()
        return ""


class CertificateError(CertToolError):
    """Base exception class for all Certificate exceptions."""
