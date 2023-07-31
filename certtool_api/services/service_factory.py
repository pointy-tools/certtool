# from logging import getLogger

# from certtool_api.core import Certificate
# from certtool_api.repositories import RepoFactory
# from certtool_api.services import CookieMonsterService
#
# from .protocols import CookieSaver, CookieTerrorizer
#
# DEFAULT_MONSTER_APPETITE = 8
# DEFAULT_SERVICE_LOGGER = getLogger()


class CookieMonsterServiceFactory:
    """In this example, CookieMonsterServiceFactory builds the CookieMonsterService, which
    allows for flexible, on the fly configuration of the service.

    If it's decided the storage of cookies should be done by a separate service and
    now requires using a client to send the request, this factory can be updated to pass in the client
    and, as long as the client fulfills the CookieSaver protocol, the CookieMonsterService won't realize a difference.

    What will likely happen _more often_ is a setting needs to be adjusted, say, a monster's default appetite depending
    on ~provider~, I mean, environment.

    Using a factory and constants that could be tied to settings, env vars, or any other calculations simplifies and
    contains this logic, again, not concerning the monster service itself with the complexity.
    """


#    @staticmethod
#    def cookie_monster_service(
#        monster: CookieTerrorizer = None, repository: CookieSaver = None
#    ) -> CookieMonsterService:
#        if monster is None:
#            monster =
#        if repository is None:
#            repository = RepoFactory.cookie()
#        return CookieMonsterService(
#            monster=monster, repository=repository, log=DEFAULT_SERVICE_LOGGER
#        )
