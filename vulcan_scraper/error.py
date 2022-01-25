from logging import getLogger


class ScraperException(Exception):
    def __init__(self, *args: object):  # this is weird
        if args:
            super().__init__(*args)
            getLogger(__name__).debug(f'{self.__class__.__name__}: {", ".join(args)}')
        else:
            super().__init__()
            getLogger(__name__).debug(f"{self.__class__.__name__}")


class HTTPException(ScraperException):
    def __init__(self, verb: str, url: str, status_code: int):
        self.verb = verb
        self.url = url
        self.status_code = status_code
        super().__init__(f"{verb} {url} got status code {status_code}")


class VulcanException(ScraperException):
    pass


class NotLoggedInException(ScraperException):
    pass


class InvalidSymbolException(VulcanException):
    pass


class ServiceUnavailableException(VulcanException):
    pass


class LoginException(ScraperException):
    pass


class NoValidSymbolException(LoginException):
    pass


class BadCredentialsException(LoginException):
    pass
