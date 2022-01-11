from logging import getLogger


class ScraperException(Exception):
    def __init__(self, *args: object):  # this is weird
        if args:
            super().__init__(*args)
            getLogger(__name__).error(f'{self.__class__.__name__}: {", ".join(args)}')
        else:
            super().__init__()
            getLogger(__name__).error(f"{self.__class__.__name__}")


class HTTPException(ScraperException):
    pass


class VulcanException(ScraperException):
    pass


class NotLoggedInException(ScraperException):
    pass


class ServiceUnavailableException(VulcanException):
    pass


class LoginException(ScraperException):
    pass


class NoValidSymbolException(LoginException):
    pass


class BadCredentialsException(LoginException):
    pass
