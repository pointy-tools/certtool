import unittest

# will be using localstack for these functional tests
import boto3
from certtool_api.services.kms_service import DEFAULT_KMS_KEY_ALIAS, KMSService

ENDPOINT_URL = "http://localstack:4566"
AWS_CREDS = {
    "aws_access_key_id": "test",
    "aws_secret_access_key": "test",
}


class KMSServiceFunctionalTestCase(unittest.TestCase):
    def _create_kms_key(self):
        return self.client.create_key()["KeyMetadata"]["Arn"]

    def _create_kms_alias(self, key_id):
        self.client.create_alias(AliasName=DEFAULT_KMS_KEY_ALIAS, TargetKeyId=key_id)

    def _delete_kms_key(self, key_id):
        self.client.schedule_key_deletion(KeyId=key_id, PendingWindowInDays=7)

    def _delete_kms_alias(self, key_alias=DEFAULT_KMS_KEY_ALIAS):
        self.client.delete_alias(AliasName=key_alias)

    def setUp(self):
        self.client = boto3.client("kms", endpoint_url=ENDPOINT_URL, **AWS_CREDS)
        self.key_id = self._create_kms_key()
        self._create_kms_alias(self.key_id)
        self.test_token = b"test"

    def tearDown(self):
        self._delete_kms_alias()
        self._delete_kms_key(self.key_id)

    def test_encrypt_decrypt(self):
        kms = KMSService(endpoint_url=ENDPOINT_URL)
        blob = kms.encrypt(self.test_token)
        self.assertEqual(kms.decrypt(blob), self.test_token)

    # TODO: Move this test to a integration test, can't rely on localstack to use the context at all
    def test_encrypt_with_encryption_context(self):
        encryption_context = {"test": "test"}
        kms = KMSService(
            endpoint_url=ENDPOINT_URL, encryption_context=encryption_context
        )
        blob = kms.encrypt(self.test_token)
        self.assertEqual(kms.decrypt(blob), self.test_token)
        with self.assertRaises(Exception):
            kms.decrypt(blob, {"test": "test1"})
