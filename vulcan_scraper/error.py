class ScraperException(Exception):
    pass


class HTTPException(ScraperException):
    pass


class VulcanException(ScraperException):
    pass


class ServiceUnavailableException(VulcanException):
    pass


class LoginException(ScraperException):
    pass


class NoValidSymbolException(LoginException):
    pass


class BadCredentialsException(LoginException):
    pass
