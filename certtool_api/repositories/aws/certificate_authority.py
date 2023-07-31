from typing import TYPE_CHECKING

from attrs import define
from certtool_api.core import Certificate, CertToolError

if TYPE_CHECKING:
    from mypy_boto3_acm_pca import ACMPCAClient
    from mypy_boto3_acm_pca.waiter import CertificateIssuedWaiter

import boto3


# class to interact with the ACM Private CA
@define
class AWSCertificateAuthority:
    """
    This class is used to interact with the ACM Private CA

    :param arn: The arn of the certificate authority
    :param valid_days: The number of days certificates signed by this authority should be valid for
    :param signing_algorithm: The signing algorithm to use
    :param profile_name: The name of the AWS profile to use

    :Example:

    >>> from certtool_api.core import CertificateAuthority
    >>> ca = CertificateAuthority(arn="arn:aws:acm-pca:us-east-1:123456789012:certificate-authority/11111111-2222-3333-4444-555555555555")
    >>> ca.issue_certificate(certificate=cert)
    """

    arn: str
    valid_days: int = 365 * 5  # 5 years
    signing_algorithm: str = "SHA512WITHRSA"
    _profile_name: str | None = None

    @property
    def _client(self) -> "ACMPCAClient":
        return boto3.session.Session(profile_name=self._profile_name).client("acm-pca")

    def get_certificate(self, certificate_arn: str) -> Certificate:
        resp: dict = self._client.get_certificate(
            CertificateAuthorityArn=self.arn, CertificateArn=certificate_arn
        )
        cert: Certificate = Certificate(
            private_ca_arn=certificate_arn,
        )
        cert.certificate_pem = resp["Certificate"].encode()
        cert.chain_pem = resp["CertificateChain"].encode()
        return cert

    def issue_certificate(
        self, certificate: Certificate, valid_days: int | None
    ) -> Certificate:
        if not valid_days:
            valid_days = self.valid_days
        client: "ACMPCAClient" = self._client
        resp: dict = client.issue_certificate(
            CertificateAuthorityArn=self.arn,
            Csr=certificate.csr_pem.decode(),
            SigningAlgorithm=self.signing_algorithm,
            Validity={
                "Value": valid_days,
                "Type": "DAYS",
            },
        )
        certificate.issuer_ca_arn = self.arn
        certificate.private_ca_arn = resp["CertificateArn"]
        waiter: CertificateIssuedWaiter = client.get_waiter("certificate_issued")
        waiter.wait(
            CertificateAuthorityArn=certificate.issuer_ca_arn,
            CertificateArn=certificate.private_ca_arn,
        )
        signed_cert: Certificate = self.get_certificate(
            certificate_arn=certificate.private_ca_arn
        )
        certificate.certificate = signed_cert.certificate
        certificate.chain = signed_cert.chain
        return certificate


# error class for the ACM Private CA
class AWSCertificateAuthorityError(CertToolError):
    """
    This class is used to represent errors interacting with the ACM Private CA
    """
