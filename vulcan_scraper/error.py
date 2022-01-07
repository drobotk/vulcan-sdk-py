import re
from logging import getLogger
from bs4 import BeautifulSoup, element


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


def tag_own_textcontent(tag: element.Tag) -> str:
    return re.sub("\s+", " ", "".join(tag.findAll(text=True, recursive=False))).strip()


# sdk/ErrorInterceptor.kt <3
def check_for_vulcan_error(text: str):
    soup = BeautifulSoup(text, "lxml")

    s = soup.select(".errorBlock .errorTitle, .errorBlock .errorMessage")
    if s:
        raise VulcanException(f"{s[0].text}. {s[1].text}")

    # login errors
    s = soup.select(".ErrorMessage, #ErrorTextLabel, #loginArea #errorText")
    for tag in s:
        msg = re.sub("\s+", " ", tag.text).strip()
        if msg:
            raise BadCredentialsException(msg)

    s = soup.select("#MainPage_ErrorDiv div")
    if s:
        tag = s[0]
        own = tag_own_textcontent(tag)
        if (
            "Trwa aktualizacja bazy danych" in tag.text
            or "czasowo wyłączona" in tag.text
        ):
            raise ServiceUnavailableException(own)
        else:
            raise VulcanException(own)
