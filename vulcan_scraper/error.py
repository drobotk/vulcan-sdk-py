class ScraperException( Exception ):
    pass

class HTTPException( ScraperException ):
    pass

class VulcanException( ScraperException ):
    pass

class LoginError( ScraperException ):
    pass

class NoValidSymbolError( LoginError ): 
    pass

class InvalidCredentialsError( LoginError ):
    pass