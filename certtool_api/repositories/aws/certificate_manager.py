# This module implements a wrapper around boto3's acm client to interact with ACM for ticket signing, requesting and interacting with stored certificates.

import secrets
from typing import TYPE_CHECKING

from attrs import define
from certtool_api.core import Certificate, CertToolError
from certtool_api.core.aws.certificate_authority import AWSCertificateAuthority

if TYPE_CHECKING:
    from mypy_boto3_acm import ACMClient
    from mypy_boto3_acm.waiter import CertificateValidatedWaiter

import boto3


@define
class AWSCertificateManager:
    """
    This class is used to manage certificates in ACM
    """

    signing_algorithm: str = "SHA512WITHRSA"
    key_algo: str = "RSA_2048"
    _profile_name: str | None = None
    _private_ca: AWSCertificateAuthority | None = None

    @property
    def _client(self) -> "ACMClient":
        """
        This method is used to get an ACM client

        :return: The ACM client
        """
        return boto3.session.Session(profile_name=self._profile_name).client("acm")

    def export_certificate(self, certificate_arn: str) -> Certificate:
        """
        This only works on private certificate requested via ACM. ie certificates in ACM listed as Private are valid targets
        """
        passphrase: bytes = secrets.token_hex().encode()
        resp: dict = self._client.export_certificate(
            CertificateArn=certificate_arn, Passphrase=passphrase
        )
        cert: Certificate = Certificate(
            acm_arn=certificate_arn,
            cert_pem=resp["Certificate"].encode(),
            chain_pem=resp["CertificateChain"].encode(),
        )
        cert.set_key_pem(key_pem=resp["PrivateKey"].encode(), passphrase=passphrase),
        return cert

    def request_certificate(self, certificate: Certificate) -> Certificate:
        """
        This method is used to request a certificate from ACM that is signed by our private CA but managed by ACM (i.e. it will be automatically renewed)

        :param certificate: The certificate to request
        :return: The requested certificate

        :raises CertificateManagerError: If there is an error requesting the certificate

        :Example:

        >>> from certtool_api.core import Certificate
        >>> from certtool_api.services import CertificateManager
        >>> from certtool_api.services import CertificateManagerFactory
        >>> certificate = Certificate()
        >>> manager: CertificateManager = CertificateManagerFactory.manager()
        >>> requested_certificate = manager.request_certificate(certificate)  # doctest: +SKIP
        """
        if not self._private_ca:
            raise AWSCertificateManagerError("No private CA configured")
        idemp_token: str = secrets.token_hex()[0:32]
        client: ACMClient = self._client
        try:
            response = client.request_certificate(
                DomainName=certificate.subject.common_name,
                CertificateAuthorityArn=self._private_ca.arn,
                SubjectAlternativeNames=certificate.alternative_names,
                KeyAlgorithm=self.key_algo,
                SigningAlgorithm=self.signing_algorithm,
                IdempotencyToken=idemp_token,
                Tags=certificate.tags,
            )
        except Exception as e:
            raise AWSCertificateManagerError("Error requesting certificate") from e
        cert_arn: str = response["CertificateArn"]
        waiter: CertificateValidatedWaiter = client.get_waiter("certificate_validated")
        waiter.wait(CertificateArn=cert_arn)
        signed_cert: Certificate = self.export_certificate(cert_arn=cert_arn)
        certificate.acm_arn = signed_cert.acm_arn
        certificate.certificate = signed_cert.certificate
        certificate.chain = signed_cert.chain
        certificate.key = signed_cert.key
        certificate.issuer_ca_arn = self._private_ca.arn
        certificate.attrs_from_x509_certificate()
        return certificate


class AWSCertificateManagerError(CertToolError):
    """
    Base exception class for all CertificateManager exceptions.
    """
