import datetime
import unittest

from certtool_api.core import Certificate, Subject
from cryptography import x509
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

# from cryptography.x509 import Certificate as X509Certificate
# from cryptography.x509 import CertificateSigningRequest
# from cryptography.x509.base import CertificateSigningRequestBuilder
from cryptography.x509.oid import NameOID

DEFAULT_SUBJECT = Subject(
    common_name="test",
    organization="test",
    organizational_unit="test",
    locality="test",
    state="test",
    country="test",
    email="test@test.com",
)


def generate_test_key_pem(password: str | None = None) -> bytes:
    """
    This method is used to generate a test key

    :return: The test key
    """
    key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    if password:
        encryption_algorithm = serialization.BestAvailableEncryption(password.encode())
    else:
        encryption_algorithm = serialization.NoEncryption()
    return key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=encryption_algorithm,
    )


TEST_KEY_PEM_NOPASS = (
    b"-----BEGIN RSA PRIVATE KEY-----\nMIIJKAIBAAKCAgEAmpHbOtP+zbVgJzOx3mtx"
    b"E47aHbskK4i5sLJhiIhvmUypFQtc\nBsfHr6kK/2e6eKG+I5qZ3ZzkFQcVEPN9I+CbM/M"
    b"EhYTm89BEfT410MeVZn+TDepb\n3X2rBsgr4CbqBD4EqM4wdX1q6GoWrcsxc30GUMEBBi"
    b"HTwgPYEDELRc71XROQJ3gL\nS3EJ1AWt00qEpUWMp4Sh2kdbMvf7ypNfvJBAJfQGQyVQW"
    b"ptLC5wh4lH0ZV2z1qJ+\nSb+Q73IO4ipy8OhBgN03BhbLOb4lvo1kBevE3srGv/qPqnSZ"
    b"+vnanf4rQQ8IDNaZ\nR1ifEJx73yt496+6KxqDiMHG5gJVOEpcjKYgIbCbcs5Zoj+EERq"
    b"mGZN/BR/nFfQW\nqO0vSNe60GiaEk8gTQ5Y9Xggawp53/M/TQ9G+Rx1h29JE1eIArLeq4"
    b"UMfF8TcMkV\nwfZtWXdn1h7D4cKhWW5SquDtVWez5KjzXtaaFjcfgL4QOVQJchZoWkS/l"
    b"A+0l8SQ\nwMOXuov0ZcJgnBaO7/xsW3B/qksTrBu0E2xt+1erNRnaI8eULOND7zZR0OXG"
    b"wi/d\nEBKSB+7cVKe8jrU172CYLCDpQ87nF29HNRbA8oU0phXIVPZRqJ/KZeX3hGsnliY"
    b"/\nNxpQnl/OZLuH/byC8t1cSkQGASxalbzbDf3Pn6vqGXWgO2oxj0h6A/2PgDcCAwEA\nA"
    b"QKCAgBAIVn7G2/xe1pMiYc3yA4fVjqq8TU9lrmsVSZgVnMvAH56i77/1S3FdPZq\nJ2hX"
    b"movgC8nhB7IeA1U7NjrqgssCD8cFerGz4Oo5qHD9kYEsCKxDrsO0ruohozWJ\nB7w6TFz"
    b"0iK/UX1fW3AVS0CZRS0MuiBVbrPdF3QBtH1wU95wXpQE/TvAoudqhDEYl\njxpf0+5apo"
    b"3cmZR+HiNq1iB3hMYIuSlL/JRNM3c8dugcFXK4B9uQptSM1p1Uq1b/\ngSs1Rre+tomYz"
    b"iY9a+YPHGyuhDanVSyHBHdM+pnUZovM12Ks2Ia3hOYNkvhUFQjT\n/B5xbYhpT9PZDsTu"
    b"M3OWKkwh0t8rVWtCRK0GsohYIlVdniX628qBBj2ZUAKZA7KF\nUiQ3yheFEPN/vkEO3Lr"
    b"Y+XGvABVwQCAyP3DvfDHHXjCyZrlcX4AqLOYysvzh3C3N\n3qZrZ/B4sL/3iclmU4PFTD"
    b"ZN7VZbKROtbhKi5YrQTujSsKv+23R0ay9gegunKeaa\nuetNDdA9YKw9RV3AZDIAOZm9s"
    b"NJ5cBaaBcblCZQSLl7mk4+jeVgyyKvJSa1DJspC\nUyibgoNHnfm8bGkmm4a3EVBQTv/u"
    b"aumv641xEl1UpbUmlM1fixfqW07T13/lcgD+\niWII52MnnGBVniPbahdPcNjJJFpa0ip"
    b"Uq0gaTD3mjcbz8f75WQKCAQEA2kBY5d95\n6NliNNeSBcK3Qt6VutV5RvumKaLeV7igjY"
    b"xSJxQHBhO7eYbkIbrn1DLQY2XNSP2Q\nuWDtU5//JroaAmsFVfhmcgPYa/oGMfvsBd2j8"
    b"l3P0Q3QHLSJFt2MZX8YtJjZOx2V\nAtIyZ1Nlm61yeD2hWmjhs+b895rZ0WvZwBB9QTrV"
    b"yv0Gn1kjY5NZ/VqoeiqHqEYR\noDIZIoijdGXhJSZenHk405YmHis1W17piQPDVmpy/Jm"
    b"wXyTNXWDpDxuNCcxczxjA\nfVwewVByGTAJvfyzqntWj2lMPNabAFMoNl14OJqhfIies1"
    b"5K6EaH12LcI7tQ2P9B\n4HQ5RGuYuB78awKCAQEAtU3WrVSDbBg4E1UYyst7GqQJU1Zfs"
    b"nEfso0YQYDgaAVT\nCBphCU0tOBzy1XmB9TAePSN53kKOr7pO3neswok5mMkhTCcC8yAp"
    b"4ZBrvKZF35nH\nTfL9JWyjpbfmiNC5lJs08zRt7rW8v0dLCnYhZTFHsuf4dgoMVV5i+ZJ"
    b"D8NLzV1t6\nwOcINNUzYUp5ZUSN/QM9meTen5lfjJK+tD8pRp9RYomMGT7SZwUtGwJTE4"
    b"KN/fiN\nPvlTXZhQq1VQ4GlRaYfDjC8GyTXZX1ZjqcFEcFW+hALBFjbqh1jkn6eKNwaHb"
    b"HF3\ncmpm+WTCcF+dQZVhgY5kYVq3DBzQCLTwmg8P1Zw+ZQKCAQB40CHlrZ1YTe1U/vew"
    b"\nBKdZdsk/kSf/KRJD/gpCWMtXT5OyWh3BOW8PyKHEIihuiGpee131x5czZvo4zlp5\nX4"
    b"9CQ2fCvSxIdOR6cP648JEodhZo9ZEyUgkfurggVid/j6lnXyzw0mFIHH8WP04B\nrTOuZ"
    b"79HwsMdyQHDNo7YpHD3JqmPUDhEk2f1EWzLlCe+XU7hwWUyuwbKvLC5MxX4\nOuU0oVbC"
    b"G0Bfr8AN9zEkERgJZnHdBjP8rD67jC26QQkB+ehKwjul0DfNrQ7BR/zB\nAJyD9Lyn5Hp"
    b"4DHvNOaa3uVCLN5ZzDvXRb/cZp1qj1Vcg3XKqvOf2Fuaqjuuceksh\nsNVdAoIBAQChL7"
    b"+xP9bLjkikX154RSmACOBFmB/iTBJrMmejLMnVkQ49wP4OP+/4\n2DvIMIuqiYoIvvaE9"
    b"FVYw+GEhY8xMMDlJcOVqYVE046IfFZcVNMANP5tPZ9z2z8u\ngO3TKwYiqU4M/srRk/9n"
    b"ayG6/kU4avSciQFrKAnJB+4khbYjb9hqDOl4gK3aEsXo\nNEbzElzN2Ui1/jUyXTAGkRw"
    b"8sX6ny9KWMUU92I1Ei+SLA6kKSmKkrYodt5o3NshZ\nWrNZoCiCEvJ2OgTldBt6WBqo/C"
    b"s1V/XV9YDmmBIwHIa9rj0CKKrTbZlNPm2oQb1g\nHJF5ki4q+YYiy3y7pw4I/5x8yvE/7"
    b"vXFAoIBADiQ4YAO9OC80Pgqq69hwzMktX4R\nudT31WGWbjnHk0bw22mmAxOcmJezCfiy"
    b"FLDCDjrXwDilD+s0oBzhM40oxZNEDH/0\nKCKN4+ksVpV7V9dx73Zwg7I3YI4gMVNEiWl"
    b"QN2A2vR94d3KkR+utakj3DrGtC6aA\n8aWr2IIYG8LHvbpRb/K7Gg1oogJ1lRuWVGz1k/"
    b"zwNZqI1rNvOLC366jkFei/jYZc\n6xKJio/Vk7k1UjXqP8dgbL0/RY1xwcQv7ImwNqziQ"
    b"kCNLYijl84ZyA+y3DW0AMTN\nbwMAE+5wVZoNg+zplVk9aqgqAKiwUEzn7wD1k3w3kRgx"
    b"VPYxZvGJJl5nD/0=\n-----END RSA PRIVATE KEY-----\n"
)
TEST_KEY_PASSWORD = "testpassword"
TEST_KEY_PEM_WITHPASS = (
    b"-----BEGIN RSA PRIVATE KEY-----\nProc-Type: 4,ENCRYPTED\nDEK-Info: AES"
    b"-256-CBC,1B32B777FCE77B28813CE31C21E5A6CA\n\na0HftERVpG8KL2J1zacxWUBld"
    b"diXRoCg0/2NCITLM97cG/giEeTDDm7kkQWPSGUy\nnfRApLW/Lue8RiPxpb6PTE1+Kh+O"
    b"So/eOAxqRYIfSxJhrdqhdaLTo2fyvN0fE5h6\nDoXlraqQ0ku/8XkP0CQ5NuQuoLE878B"
    b"wo6PA/EeN1FCqT20OuzsgNaAcsVPylbQK\nzfPcvszdzva0974y6hducmis2NQG6jdHDb"
    b"ZDhfdbown84Vc5Az8edZ/PsL1DkvKW\noZWsBKMvNKjNDgb/HZ7rZqmVCVm4jdwN2PLeY"
    b"DwGon+TIy3NTAfkxwFx/EbeoV5f\n3nsSBQXqzLpK3H/dkAqbvvy+Xq555fsXv6vRW3tN"
    b"eZ8lr1Tsgo8/huGAn7WgG5Vq\nme/ydZ18ZYOtQkMW5r9fYpchhfhI4Uc9heBqWdc2eeu"
    b"1NSS/ZMPaBAaq6dkyNdAA\nurVP2rchYOgkgti9kxX+3jXJ4Z/0c8CCBxenlNg5IAf/H+"
    b"n78N59cgVn3wwsW6dr\nTyWVsjN/RIcssJriYWYDBrPyEh2oKhxb2wwL+0W6EMkNKutNh"
    b"dIq49+lVReTKK3r\nqfLZnm5vqDUk1tQ4CvQQ/3vYTt5q556EvzErizNpNbWVrRTaiuBq"
    b"2NGA3JDPt51X\nOgR6AovrSoXkXuOhinR/79Ttq36f1giAT04R+qBPQlNRTUA9N1lzLgO"
    b"eYE8ztn8T\nUwSAQTBvcsbustMtlBCJXXgWA+L2ZChSKFw9Ucz+nPMFMqkVqNZKwRzivZ"
    b"qAA2Fw\nW6um/iz/UBTqTqdODwEVYe8I9wJUWCsNuywfOPI9JP9NrCXwTkf7kAQhnTNWW"
    b"JY0\nlLImVQgcpBG4ycVDvKw764JnABZqmQpccBU+d0pAoJttnJv7QxSWxTKcdziSCxbm"
    b"\nxvW9rt99GQ6FLcLbbX9WW1knQw9I7FJT/OnINgXEwW9yq3MFShd95WMTVTFpo7j1\noH"
    b"gq7fLPf7ZOH9Y1JicrksZuFzEF3n0chvFO6dpgxoOui2Z5KMhAXF/JleEGJCee\n8Zqcm"
    b"Gx9rnna6+tnCjEYH/uQxYKsXGHJSuiK4xRFJvHSSNifXtNKVL93eZxJE5ia\n5uldMxXG"
    b"l4G09H7bBE9gGGkp1n2I+0Z4ZQ3u1VJhcgofzFrCcOKPV0f5WKkqzP8l\nXQbV6oN3ZtL"
    b"mzPII0e/fyeN2wVnupXoSf3Os3LLcQNFt5rGEhBESdIcA8p/pJ111\n4/82Fq4l198a3i"
    b"65onyy4CaREZcBD/mlJj2E+2I+fwvINf/VxCqUPvIxzi+JKSfC\ne/VYbkf6JWdPv6BOE"
    b"kFsGzUuDRTj8YEEU7if6sJ5TT1km+cY9Toixa1Zt3jIpIXw\nmnR3p5Lc71+kwqyD/M0P"
    b"BPJ8p1c89MIzQlL5+h4yLvjSoVN5lTyMym7qYJPBzBpa\nx/sJxaJKsI/yTa0F5ZbNwg0"
    b"IM8qaYGWyyBQqFIqxbEm7bh/W8vgI8KE4ISzPIqwK\nCj7M096bYEdwLFjWqf1e62flRQ"
    b"G5NXWTBNkoYXuUPH6YzWEPZmPE5BUTNUiei27i\nmz2QpvlalwNl/Pa0p4fcgjWBNZYgj"
    b"pLGLAHa9DB2bXR04CznhyBtyO7LHridYQ0d\nagLWvcTOAwRZ1/qr1I53BMsEZzagNYRo"
    b"VyoVosRc8yUM8vrKBt500Wt1+v+VhcE4\neZ/DZae9By8kteWDtO3G5f0Qa0ciRbipsFa"
    b"TIP4J4FEVzntvk9/7mCMltV4zGTV9\nvOe7Ewm2FT9ErImiZK2tqQCeNqITuMwuvXGcet"
    b"hOMsTLrxYnC8aEfNU7Chnq+qra\npo3hL0asXvh/zxax5DejfQqQjb/CnSI+Rkv9xqvIi"
    b"uk60fK5ogW8Eu7FEuOCnOJK\nxfaoQWNLpcjDIlk1hALK4yerg+PvUpITvIv2tPRcp75B"
    b"2oVf2GaGRPW+e6v/N2DA\nRN/br45rSsIZzBitCgT3qMY+9GVHBXHvNde6RCQ1qBD7J6U"
    b"ug2Lw2ppphP9ifR8R\naMWAycmi/JztdyPzHmC6k3xnAhl4cXmKykP6+y7SpuSj/Xj/om"
    b"m22y2fvs7G9Stk\nygus+i0kjaCNqacuuluuS901c7if/GZIQso464Aa2FmbI0tnQSJ2i"
    b"CkxOykMb5lw\ndVVcV+tGE8FZ/L5+APO/NQIcN81hUXQCCaI28qMfXnYq7VG0F9f+tC4J"
    b"1SQ7RMTj\n20jVkykwDCkOdIVeNA4o9u2tUlqD17CRPirDjXGX26vbJ/LYnbV0qlYEh6q"
    b"89iyG\nHvCcLnyEqPgrI3zhOAsmVGNG9v6Y2EXhPyxYlEsjxMMC6/4pGaP0G24aTEYxrA"
    b"BY\na7iu2qn0dRblQV+l3HTZnx4dS4FIATXku5lPClQXS1Aq5TRc3VXCUTefVNQcDMtv\n"
    b"ABVxL/kHMaYT85IOygJJX9/Bupg7NjoNugs9KzcfSWKngk0jYURemTsvAA/PxNOQ\neCG"
    b"GJueerehI2wwtxQ5EvGdXFqTNQ2GIYDTlNEmtITaNN8Ii4jBTGtqsmYgZ/PjV\nazxi/Q"
    b"e/2SGKP8ATdt2/pRaTmmTuhD/ol7nLlras7rO26ZouGzK+hQQH3GL2pAKQ\nlfRaMeIRY"
    b"kTqppzpa9ad93Dm+1S90uujPZNvn2NwSfYIE+xNwzhZHnMRlhnMOdkq\nXGBO2N7Rz9Nu"
    b"rE7VpcgpU2i6m5dyZLyKMrUmiVueMV4cSdPYXtw5anD+qMFLvUJr\nEbPbnZWDrukHDv4"
    b"fG3anFOOtnlEi+l3VBfU0yJbo5Bkp5xe2+eD8YZbTR+z0zla+\n0BYTkw1UPAcB/yEJK8"
    b"0Dc4/xQwGCsoBiy1bSmT+bFVgpF2GePfKP92zrnbM+CLhf\ndZylullQoQzYFk3wgrOMZ"
    b"RGfLPGgcGJjsfIaLG7aNktewHbA+D0e3vno9t5tHSPB\nVUMM99kutnGRxYKhkZtQsbz1"
    b"L8I/uA93tB6no6zOMCPZo8Crm1VrPrfgcl1nFmWQ\ntL4AhT1yy6/L5u8pGlOLertB5JV"
    b"m89pZxmH17zA+q8nrVgxnZyxgrGjuvA8EhnQG\n3VJAc2HCIFBcflg16X5+SiQg8M5sy1"
    b"Z/dTXxOoYPUiLgM1TQOpTiQDe3JHTYQlc1\n+4HiftDo+a6HqZr397C+3pwlcaRapVs2Z"
    b"F99CqpcrPmx7nsmdp+0NxGxVT6Uz+jx\n-----END RSA PRIVATE KEY-----\n"
)

TEST_KEY = serialization.load_pem_private_key(data=TEST_KEY_PEM_NOPASS, password=None)


def generate_test_csr(key, alternate_names):
    builder = x509.CertificateSigningRequestBuilder()
    builder = builder.subject_name(
        x509.Name(
            [
                x509.NameAttribute(NameOID.COUNTRY_NAME, DEFAULT_SUBJECT.country),
                x509.NameAttribute(
                    NameOID.STATE_OR_PROVINCE_NAME, DEFAULT_SUBJECT.state
                ),
                x509.NameAttribute(NameOID.LOCALITY_NAME, DEFAULT_SUBJECT.locality),
                x509.NameAttribute(
                    NameOID.ORGANIZATION_NAME, DEFAULT_SUBJECT.organization
                ),
                x509.NameAttribute(
                    NameOID.ORGANIZATIONAL_UNIT_NAME,
                    DEFAULT_SUBJECT.organizational_unit,
                ),
                x509.NameAttribute(NameOID.COMMON_NAME, DEFAULT_SUBJECT.common_name),
                x509.NameAttribute(NameOID.EMAIL_ADDRESS, DEFAULT_SUBJECT.email),
            ]
        )
    )
    builder = builder.add_extension(
        x509.SubjectAlternativeName([x509.DNSName(name) for name in alternate_names]),
        critical=False,
    )
    # builder = builder.sign(key, hashes.SHA256(), default_backend())
    return builder


test_csr_pem = ""
test_csr = x509.load_pem_x509_csr(data=test_csr_pem)

test_certificate_pem = ""
test_certificate = x509.load_pem_x509_certificate(data=test_certificate_pem)

test_chain_pem = ""
test_chain = x509.load_pem_x509_certificate(data=test_chain_pem)

test_common_name = "test_common_name"

test_subject_details = {
    "country": "US",
    "state": "California",
    "locality": "San Francisco",
    "organization": "Test Organization",
    "organizational_unit": "Test Organizational Unit",
    "email": "pie@pie.com",
}

test_alternate_names = ["pie.com", "pie.org"]

test_not_before = datetime.datetime(
    2018, 1, 1, 0, 0, 0, 0, tzinfo=datetime.timezone.utc
)

test_not_after = datetime.datetime(2019, 1, 1, 0, 0, 0, 0, tzinfo=datetime.timezone.utc)

test_tags = ["pie", "pie.org"]

test_key_pem_encrypted = ""

test_key_encrypted = serialization.load_pem_private_key(
    test_key_pem_encrypted, password=b"test"
)

test_certificate_fingerprint = "test_certificate_fingerprint"

test_certificate_common_name = "test_certificate_common_name"

test_certificate_subject_details = {
    "country": "US",
    "state": "California",
    "locality": "San Francisco",
    "organization": "Test Organization",
    "organizational_unit": "Test Organizational Unit",
    "email": "pie@pie.com",
}

test_certificate_alternate_names = ["pie.com", "pie.org"]

test_certificate_not_before = datetime.datetime(
    2018, 1, 1, 0, 0, 0, 0, tzinfo=datetime.timezone.utc
)

test_certificate_not_after = datetime.datetime(
    2019, 1, 1, 0, 0, 0, 0, tzinfo=datetime.timezone.utc
)

test_certificate_tags = ["pie", "pie.org"]


# unit tests for Certificate
class TestCertificate(unittest.TestCase):
    # test that the default values are set correctly
    def test_default_values(self):
        certificate = Certificate()
        self.assertIsNone(certificate.key)
        self.assertIsNone(certificate.csr)
        self.assertIsNone(certificate.certificate)
        self.assertIsNone(certificate.chain)
        self.assertIsNone(certificate.common_name)
        self.assertIsNone(certificate.subject_details)
        self.assertIsNone(certificate.alternate_names)
        self.assertIsNone(certificate.not_before)
        self.assertIsNone(certificate.not_after)
        self.assertIsNone(certificate.tags)

    # test that the key_pem property works correctly
    def test_key_pem(self):
        certificate = Certificate()
        certificate.key_pem = TEST_KEY_PEM_NOPASS
        self.assertEqual(certificate.key_pem, TEST_KEY_PEM_NOPASS)
        self.assertEqual(certificate.key, TEST_KEY)
        certificate.key_pem = test_key_pem_encrypted
        self.assertEqual(certificate.key_pem, test_key_pem_encrypted)
        self.assertEqual(certificate.key, test_key_encrypted)

    # test that the csr_pem property works correctly
    def test_csr_pem(self):
        certificate = Certificate()
        certificate.csr_pem = test_csr_pem
        self.assertEqual(certificate.csr_pem, test_csr_pem)
        self.assertEqual(certificate.csr, test_csr)

    # test that the certificate_pem property works correctly
    def test_certificate_pem(self):
        certificate = Certificate()
        certificate.certificate_pem = test_certificate_pem
        self.assertEqual(certificate.certificate_pem, test_certificate_pem)
        self.assertEqual(certificate.certificate, test_certificate)

    # test that the chain_pem property works correctly
    def test_chain_pem(self):
        certificate = Certificate()
        certificate.chain_pem = test_chain_pem
        self.assertEqual(certificate.chain_pem, test_chain_pem)
        self.assertEqual(certificate.chain, test_chain)

    # test that the fingerprint property works correctly
    def test_fingerprint(self):
        certificate = Certificate()
        certificate.certificate_pem = test_certificate_pem
        self.assertEqual(certificate.fingerprint, test_certificate_fingerprint)

    # test that the _read_certificate function works correctly
    def test_read_certificate(self):
        certificate = Certificate()
        certificate.certificate_pem = test_certificate_pem
        self.assertEqual(certificate.common_name, test_certificate_common_name)
        self.assertEqual(certificate.subject_details, test_certificate_subject_details)
        self.assertEqual(certificate.alternate_names, test_certificate_alternate_names)
        self.assertEqual(certificate.not_before, test_certificate_not_before)
        self.assertEqual(certificate.not_after, test_certificate_not_after)

    # test that the _get_subject_details function works correctly
    def test_get_subject_details(self):
        certificate = Certificate()
        certificate.certificate_pem = test_certificate_pem
        self.assertEqual(
            certificate._get_subject_details(test_certificate.subject),
            test_certificate_subject_details,
        )

    # test that the from_pem function works correctly
    def test_from_pem(self):
        certificate = Certificate.from_pem(test_certificate_pem)
        self.assertEqual(certificate.certificate_pem, test_certificate_pem)
        self.assertEqual(certificate.certificate, test_certificate)
        self.assertEqual(certificate.common_name, test_certificate_common_name)
        self.assertEqual(certificate.subject_details, test_certificate_subject_details)
        self.assertEqual(certificate.alternate_names, test_certificate_alternate_names)
        self.assertEqual(certificate.not_before, test_certificate_not_before)
        self.assertEqual(certificate.not_after, test_certificate_not_after)


if __name__ == "__main__":
    unittest.main()
