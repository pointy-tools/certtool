from attrs import define
from cryptography.x509 import Name, NameAttribute, NameOID


@define
class Subject:
    common_name: str | None = None
    country: str | None = None
    state: str | None = None
    locality: str | None = None
    organization: str | None = None
    organizational_unit: str | None = None
    email: str | None = None

    def to_x509_name(self) -> Name:
        name_list: list[NameAttribute] = []
        if self.common_name:
            name_list.append(NameAttribute(NameOID.COMMON_NAME, self.common_name))
        if self.country:
            name_list.append(NameAttribute(NameOID.COUNTRY_NAME, self.country))
        if self.state:
            name_list.append(NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, self.state))
        if self.locality:
            name_list.append(NameAttribute(NameOID.LOCALITY_NAME, self.locality))
        if self.organization:
            name_list.append(
                NameAttribute(NameOID.ORGANIZATION_NAME, self.organization)
            )
        if self.organizational_unit:
            name_list.append(
                NameAttribute(
                    NameOID.ORGANIZATIONAL_UNIT_NAME, self.organizational_unit
                )
            )
        if self.email:
            name_list.append(NameAttribute(NameOID.EMAIL_ADDRESS, self.email))
        return Name(name_list)


# ToDo: create default db entry in a migration for this
#    country_name: str = "US"
#    state_name: str = "New York"
#    locality_name: str = "New York"
#    organization_name: str = "Cedar Cares, Inc."
