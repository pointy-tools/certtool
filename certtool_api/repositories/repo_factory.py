from your_cookie_cutter_api.models import CookieModel

from .django_repository import DjangoRepository


class RepoFactory:
    @staticmethod
    def cookie() -> DjangoRepository:
        return DjangoRepository(data_model=CookieModel)
