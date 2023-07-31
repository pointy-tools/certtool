from your_cookie_cutter_api.models import CookieModel

from django_db_test_utils import DBTestCase


class CookieModelIntegrationTestCase(DBTestCase):
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

    def setUp(self):
        """
        Create two cookies, one bitten one not.
        Make sure model can pull them out in the right state.
        Then make sure models can save them in the right state.
        Modify them and make sure model saved them correctly.
        """
        bitten_cookie_model = CookieModel(is_bitten=True)
        bitten_cookie_model.save()
        whole_cookie_model = CookieModel(is_bitten=False)
        whole_cookie_model.save()
        self.bitten_cookie_model = bitten_cookie_model
        self.whole_cookie_model = whole_cookie_model

    def test_getting_bitten_cookie(self):
        bitten_cookie_model = CookieModel.objects.get(id=self.bitten_cookie_model.id)
        self.assertEqual(bitten_cookie_model.id, self.bitten_cookie_model.id)
        self.assertTrue(bitten_cookie_model.is_bitten)

        bitten_cookie = bitten_cookie_model.to_entity()
        self.assertEqual(bitten_cookie.id, bitten_cookie_model.id)
        self.assertTrue(bitten_cookie.is_bitten)

    def test_getting_whole_cookies(self):
        whole_cookie_model = CookieModel.objects.get(id=self.whole_cookie_model.id)
        self.assertEqual(whole_cookie_model.id, self.whole_cookie_model.id)
        self.assertFalse(whole_cookie_model.is_bitten)

        whole_cookie = whole_cookie_model.to_entity()
        self.assertEqual(whole_cookie.id, whole_cookie_model.id)
        self.assertFalse(whole_cookie.is_bitten)

    def test_updating_cookie_to_bitten(self):
        cookie = CookieModel.objects.get(id=self.whole_cookie_model.id).to_entity()
        cookie.bite()
        CookieModel.save_from_entity(cookie)
        newly_bitten_cookie = CookieModel.objects.get(
            id=self.whole_cookie_model.id
        ).to_entity()
        self.assertEqual(newly_bitten_cookie.id, self.whole_cookie_model.id)
        self.assertTrue(newly_bitten_cookie.is_bitten)
