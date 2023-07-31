from logging import Logger

from attrs import define
from certtool_api.core import Certificate, CertificateError

from .protocols import CertificateManager, CertificateSigner, CertificateStore


@define
class CertificateService:
    """ """

    _acm: CertificateManager

    _ca: CertificateSigner

    _repo: CertificateStore

    _log: Logger

    def sign_certificate(
        self, certificate: Certificate, acm_managed: bool = True
    ) -> Certificate:
        """
        This method is used to sign a certificate with our private CA. It supports creating both ACM managed and non-ACM managed certificates.

        :param certificate: The certificate to sign

        :return: The created certificate
        """
        self._log.info("Creating certificate")
        if acm_managed:
            try:
                certificate = self._acm.request_certificate(certificate=certificate)
            except CertificateError as e:
                self._log.error("Error creating certificate: %s", e)
                raise e
        else:
            try:
                certificate = self._ca.issue_certificate(certificate=certificate)
            except CertificateError as e:
                self._log.error("Error creating certificate: %s", e)
                raise e
        self._log.info("Certificate created")
        return certificate

    def export_certificate(self, certificate_ref: str) -> Certificate:
        """
        This method is used to export a certificate from ACM

        :param certificate_ref: The reference to the certificate to export. probably an arn

        :return: The exported certificate
        """
        self._log.info("Exporting certificate")
        try:
            certificate = self._acm.export_certificate(certificate_ref=certificate_ref)
        except CertificateError as e:
            self._log.error("Error exporting certificate: %s", e)
            raise e
        self._log.info("Certificate exported")
        return certificate
