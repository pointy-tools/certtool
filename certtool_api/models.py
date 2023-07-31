from certtool_api.core import Certificate, PrivateKey, Status, Subject, Tags
from django.db import models  # noqa: F401
from django.forms.models import model_to_dict


# model for the PrivateKey object
class PrivateKeyModel(models.Model):
    """
    Model for the PrivateKey object
    """

    private_key_id = models.BigAutoField(primary_key=True)
    kms_encrypted_key = models.BinaryField()
    kms_encryption_context = models.JSONField()

    def to_entity(self) -> PrivateKey:
        """
        This method is used to convert the PrivateKeyModel to a PrivateKey entity

        :return: The PrivateKey entity
        """
        return PrivateKey(
            private_key_id=self.private_key_id,
            kms_encrypted_key=self.kms_encrypted_key,
            kms_encryption_context=self.kms_encryption_context,
        )

    @classmethod
    def from_entity(cls, entity: PrivateKey) -> "PrivateKeyModel":
        """
        This method is used to convert a PrivateKey entity to a PrivateKeyModel

        :param entity: The PrivateKey entity to convert

        :return: The PrivateKeyModel
        """
        return cls(
            private_key_id=entity.private_key_id,
            kms_encrypted_key=entity.kms_encrypted_key,
            kms_encryption_context=entity.kms_encryption_context,
        )


# class defining a django model from the certtool_api.Certificate entity and saving all fields to the database
class CertificateModel(models.Model):
    certificate_id = models.BigAutoField(primary_key=True)
    acm_arn = models.CharField(max_length=2048, blank=True, null=True)
    private_ca_arn = models.CharField(max_length=2048, blank=True, null=True)
    issuer_ca_arn = models.CharField(max_length=2048, blank=True, null=True)
    subject_common_name = models.CharField(max_length=64, blank=True, null=True)
    subject_country = models.CharField(max_length=64, blank=True, null=True)
    subject_state = models.CharField(max_length=64, blank=True, null=True)
    subject_locality = models.CharField(max_length=64, blank=True, null=True)
    subject_ogranization = models.CharField(max_length=255, blank=True, null=True)
    subject_organizational_unit = models.CharField(
        max_length=255, blank=True, null=True
    )
    subject_email = models.CharField(max_length=255, blank=True, null=True)
    certificate_pem = models.TextField()
    chain_pem = models.TextField(blank=True, null=True)
    csr_pem = models.TextField(blank=True, null=True)
    not_before = models.DateTimeField(blank=True, null=True)
    not_after = models.DateTimeField(blank=True, null=True)
    private_key_id = models.ForeignKey(
        PrivateKeyModel, on_delete=models.CASCADE, related_name="certificates"
    )
    status = models.CharField(
        max_length=255, choices=Status.choices(), blank=True, null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # method to get the tags for a certificate
    @property
    def tags(self) -> Tags:
        return Tags(
            **{
                record.tag_key: record.tag_value
                for record in self._tags.all().iterator()
            }
        )

    # method to set the tags for a certificate
    @tags.setter
    def tags(self, tags: Tags) -> None:
        tag_models: list[TagsModel] = []
        for tag in tags.list():
            tagmod: TagsModel
            tagmod, _ = TagsModel.objects.update_or_create(
                certificate_id=self,
                tag_key=tag["Key"],
                tag_value=tag["Value"],
                defaults={
                    "tag_key": tag["Key"],
                    "tag_value": tag["Value"],
                    "certificate_id": self,
                },
            )
            tag_models.append(tagmod)
        for tag in set(self._tags.all()) - set(tag_models):
            tag.delete()
        self._tags.set(tag_models)

    # method to set the alternate names for a certificate
    @property
    def alternate_names(self) -> list[str]:
        return [
            record.alternate_name for record in self._alternate_names.all().iterator()
        ]

    # method to set the alternate names for a certificate
    @alternate_names.setter
    def alternate_names(self, alternate_names: list[str]) -> None:
        alternate_name_mods: list[SubjectAlternateNameModel] = []
        for alternate_name in alternate_names:
            alternate_name_mod: SubjectAlternateNameModel
            alternate_name_mod, _ = SubjectAlternateNameModel.objects.update_or_create(
                certificate_id=self,
                alternate_name=alternate_name,
                defaults={"alternate_name": alternate_name, "certificate_id": self},
            )
            alternate_name_mods.append(alternate_name_mod)
        for alternate_name in set(self._alternate_names.all()) - set(
            alternate_name_mods
        ):
            alternate_name.delete()
        self._alternate_names.set(alternate_name_mods)

    # method to convert a Certificate entity to a CertificateModel
    @classmethod
    def from_entity(cls, certificate: Certificate) -> "CertificateModel":
        cert_model: CertificateModel = cls(
            certificate_id=certificate.certificate_id,
            acm_arn=certificate.acm_arn,
            private_ca_arn=certificate.private_ca_arn,
            issuer_ca_arn=certificate.issuer_ca_arn,
            subject_common_name=certificate.subject.common_name,
            subject_country=certificate.subject.country,
            subject_state=certificate.subject.state,
            subject_locality=certificate.subject.locality,
            subject_ogranization=certificate.subject.organization,
            subject_organizational_unit=certificate.subject.organizational_unit,
            subject_email=certificate.subject.email,
            certificate_pem=certificate.get_pem_safe("certificate"),
            chain_pem=certificate.get_pem_safe("chain"),
            csr_pem=certificate.get_pem_safe("csr"),
            not_before=certificate.not_before,
            not_after=certificate.not_after,
            key_reference=certificate.key_reference,
            status=certificate.status,
        )
        cert_model.tags = certificate.tags
        cert_model.alternate_names = certificate.alternate_names
        return cert_model

    # method to convert a CertificateModel to a Certificate entity
    def to_entity(self) -> Certificate:
        cert: Certificate = Certificate(
            certificate_id=self.certificate_id,
            acm_arn=self.acm_arn,
            private_ca_arn=self.private_ca_arn,
            issuer_ca_arn=self.issuer_ca_arn,
            subject=Subject(
                common_name=self.subject_common_name,
                country=self.subject_country,
                state=self.subject_state,
                locality=self.subject_locality,
                organization=self.subject_ogranization,
                organizational_unit=self.subject_organizational_unit,
                email=self.subject_email,
            ),
            not_before=self.not_before,
            not_after=self.not_after,
            key_reference=self.key_reference,
            tags=self.tags,
            alternate_names=self.alternate_names,
            status=self.status,
        )
        if self.certificate_pem:
            cert.certificate_pem = self.certificate_pem.encode()
        if self.csr_pem:
            cert.csr_pem = self.csr_pem.encode()
        if self.chain_pem:
            cert.chain_pem = self.chain_pem.encode()
        return cert

    # method to convert a Certificate to dict compatible with CertificateModel.objects.update_or_create defaults
    @staticmethod
    def certificate_to_dict(certificate: Certificate) -> dict:
        return {
            "acm_arn": certificate.acm_arn,
            "private_ca_arn": certificate.private_ca_arn,
            "issuer_ca_arn": certificate.issuer_ca_arn,
            "subject_common_name": certificate.subject.common_name,
            "subject_country": certificate.subject.country,
            "subject_state": certificate.subject.state,
            "subject_locality": certificate.subject.locality,
            "subject_ogranization": certificate.subject.organization,
            "subject_organizational_unit": certificate.subject.organizational_unit,
            "subject_email": certificate.subject.email,
            "certificate_pem": certificate.get_pem_safe("certificate"),
            "chain_pem": certificate.get_pem_safe("chain"),
            "csr_pem": certificate.get_pem_safe("csr"),
            "not_before": certificate.not_before,
            "not_after": certificate.not_after,
            "key_reference": certificate.key_reference,
            "status": certificate.status,
        }

    # method to convert a CertificateModel to dict compatible with CertificateModel.objects.update_or_create defaults
    def to_dict(self) -> dict:
        return model_to_dict(self)

    # method to convert a list of Certificate entities to a list of CertificateModels
    @classmethod
    def from_entities(cls, certificates: list[Certificate]) -> list["CertificateModel"]:
        return [cls.from_entity(certificate) for certificate in certificates]

    # method to convert a list of CertificateModels to a list of Certificate entities
    def to_entities(self) -> list[Certificate]:
        return [certificate.to_entity() for certificate in self]

    # method to write TagsModel objects to the database
    def _write_tags(self) -> None:
        if self.tags:
            for tag in self.tags.list():
                TagsModel.objects.update_or_create(
                    certificate_id=self,
                    tag_key=tag["Key"],
                    defaults={
                        "tag_key": tag["Key"],
                        "tag_value": tag["Value"],
                        "certificate_id": self,
                    },
                )

    # method to write SubjectAlternateNameModel objects to the database
    def _write_alternate_names(self) -> None:
        if self.alternate_names:
            for alternate_name in self.alternate_names:
                SubjectAlternateNameModel.objects.update_or_create(
                    certificate_id=self,
                    alternate_name=alternate_name,
                    defaults={
                        "alternate_name": alternate_name,
                        "certificate_id": self,
                    },
                )

    # override save method to save the tags and alternate names to the database
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self._write_tags()
        self._write_alternate_names()

    # method to save a CertificateModel from a Certificate entity
    @classmethod
    def save_from_entity(cls, certificate: Certificate) -> "CertificateModel":
        cert: CertificateModel
        cert, _ = cls.objects.update_or_create(
            certificate_id=certificate.certificate_id,
            defaults=cls.certificate_to_dict(certificate),
        )
        if cert.tags != certificate.tags:
            cert.tags = certificate.tags
            cert._write_tags()
        if cert.alternate_names != certificate.alternate_names:
            cert.alternate_names = certificate.alternate_names
            cert._write_alternate_names()
        return cert


# class for the Certificates subject alternate names that will be referenced by the CertificateModel
class SubjectAlternateNameModel(models.Model):
    alternate_name_id = models.BigAutoField(primary_key=True)
    certificate_id = models.ForeignKey(
        CertificateModel, on_delete=models.CASCADE, related_name="_alternate_names"
    )
    alternate_name = models.CharField(max_length=255)


class TagsModel(models.Model):
    tag_id = models.BigAutoField(primary_key=True)
    certificate_id = models.ForeignKey(
        CertificateModel, on_delete=models.CASCADE, related_name="_tags"
    )
    tag_key = models.CharField(max_length=255)
    tag_value = models.CharField(max_length=255)
