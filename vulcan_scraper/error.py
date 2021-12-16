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

class NotLoggedInException( ScraperException ):
    pass
    
class NotInitializedException( ScraperException ):
    pass
    
class InitializationException( ScraperException ):
    pass
    
class NoInstanceSelectedException( ScraperException ):
    pass

class NoStudentSelectedException( ScraperException ):
    pass
    
class NoPeriodSelectedException( ScraperException ):
    pass