from your_cookie_cutter_api.core import Cookie
from your_cookie_cutter_api.models import CookieModel
from your_cookie_cutter_api.repositories import DjangoRepository

from django_db_test_utils import DBTestCase


class CookieRepositoryIntegrationTestCase(DBTestCase):
    """
    Integration test cases focus on making sure systems
    work together to help ensure those systems will
    continue to work together in production.
    These tests require exercising infrastructure
    (network calls, db transactions) so think of them
    as expensive, write only enough to confirm system
    harmony, and use them sparingly.
    """

    use_celery = False

    def test_repo_can_crud_cookies(self):
        cookie = Cookie()
        repo = DjangoRepository(data_model=CookieModel)
        repo.save(cookie)
        cookies: list[Cookie] = repo.all()
        self.assertEqual(len(cookies), 1)
        self.assertEqual(cookie.is_bitten, cookies[0].is_bitten)
        self.assertIsNotNone(cookies[0].id)
        fetched_cookie: Cookie = repo.get(id=cookies[0].id)
        self.assertIsNotNone(fetched_cookie)
        self.assertIsNotNone(fetched_cookie.id)
        self.assertEqual(cookie.is_bitten, fetched_cookie.is_bitten)
        fetched_cookie.bite()
        repo.save(fetched_cookie)
        updated_cookie: Cookie = repo.get(id=fetched_cookie.id)
        self.assertIsNotNone(updated_cookie)
        self.assertEqual(fetched_cookie.id, updated_cookie.id)
        self.assertEqual(fetched_cookie.is_bitten, updated_cookie.is_bitten)
