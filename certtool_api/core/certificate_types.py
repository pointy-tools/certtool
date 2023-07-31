from enum import Enum
from typing import TypedDict


class CertType(TypedDict):
    template: str


class CertificateType(Enum):
    Server = CertType(template="server")
    Client = CertType(template="client")
