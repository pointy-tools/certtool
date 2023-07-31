import unittest

from attrs import define
from your_cookie_cutter_api.core import Cookie, CookieMonster, CookieMonsterError
from your_cookie_cutter_api.services import (
    CookieMonsterService,
    CookieMonsterServiceError,
    CookieMonsterServiceFactory,
    LetLooseCookieMonsterError,
)


@define
class RepoFake:
    """
    Instead of a mock, we can write a small class that fulfills the CookieSaver Protocol.
    This choice can be a matter of taste, but generally one should not mock what they own.
    This fake assists tests by assuring any cookie passed is a bitten cookie while freeing
    them from the need of a db connection and the sluggishness of a db transaction.
    """

    test: unittest.TestCase

    def save(self, entity: Cookie):
        """We only save bitten cookies for our records of performance."""
        self.test.assertTrue(entity.is_bitten)


class MonsterErrorFake:
    """
    Another handy fake. Sure, mocks can be configured to have side effects as well, but
    a fake is reusable and helps document the tests.
    """

    def terrorize(self, cookie: Cookie) -> Cookie:
        raise CookieMonsterError

    def sleep_it_off(self):
        raise NotImplementedError


class CookieMonsterServiceTestCase(unittest.TestCase):
    def setUp(self):
        self.monster_error_fake = MonsterErrorFake()

        self.repo_fake = RepoFake(self)

    def _build_test_service(self, monster) -> CookieMonsterService:
        return CookieMonsterServiceFactory.cookie_monster_service(
            monster=monster,
            repository=self.repo_fake,
        )

    def test_let_loose_chomps_all_cookies_expected(self):
        monster_appetite = 3
        cookies = [Cookie() for _ in range(monster_appetite)]
        monster = CookieMonster(appetite=monster_appetite)
        service = self._build_test_service(monster)
        try:
            terrorized_cookies = service.let_loose_on(cookies)
        except CookieMonsterError as e:
            self.fail(f"CookieMonsterService unexpectedly raised exception: {e}")
        else:
            for bitten_cookie in terrorized_cookies:
                self.assertTrue(bitten_cookie.is_bitten)

    def test_let_loose_chomps_up_to_monster_appetite_and_has_monster_sleep_it_off(self):
        monster_appetite = 3
        cookies = [Cookie() for _ in range(monster_appetite + 1)]
        monster = CookieMonster(appetite=monster_appetite)
        service = self._build_test_service(monster)
        try:
            terrorized_cookies: list[Cookie] = service.let_loose_on(cookies)
        except CookieMonsterServiceError as e:
            self.fail(f"CookieMonsterService unexpectedly raised exception: {e}")
        else:
            unbitten_cookie = terrorized_cookies[-1]
            self.assertFalse(unbitten_cookie.is_bitten)
            for bitten_cookie in terrorized_cookies[:-1]:
                self.assertTrue(bitten_cookie.is_bitten)
            """If monster chomped all cookies but is still hungry then service cleaned up resources correctly."""
            self.assertTrue(monster.hungry())

    def test_let_loose_raises_error_when_exception_unexpected(self):
        cookies = [Cookie()]
        service = self._build_test_service(self.monster_error_fake)
        with self.assertRaises(LetLooseCookieMonsterError):
            service.let_loose_on(cookies)
