import re
from dataclasses import dataclass
from operator import attrgetter
from time import perf_counter
from typing import *
from bs4 import BeautifulSoup

from .enum import LoginType
from .error import *

re_valid_symbol = re.compile(r"[a-zA-Z0-9]*")


def extract_symbols(wresult: str) -> list[str]:
    try:
        soup = BeautifulSoup(wresult.replace(":", ""), "lxml")
        tags = soup.select(
            'samlAttribute[AttributeName$="Instance"] samlAttributeValue'
        )
        symbols = [tag.text.strip() for tag in tags]
        symbols = [s for s in symbols if re_valid_symbol.fullmatch(s)]

    except Exception as e:
        raise ScraperException(
            f"Extracting symbols failed: {e.__class__.__name__}: {e}"
        )

    else:
        return symbols


def extract_instances(text: str) -> list[str]:
    try:
        soup = BeautifulSoup(text, "lxml")
        tags = soup.select(
            '.panel.linkownia.pracownik.klient a[href*="uonetplus-uczen"]'
        )
        links = [a["href"] for a in tags]
        instances = [l.split("/")[4] for l in links]

    except Exception as e:
        raise ScraperException(
            f"Extracting instances failed: {e.__class__.__name__}: {e}"
        )

    else:
        return instances


def get_script_param(text: str, param: str, default: str = None) -> str:
    m = re.search(f"{param}: '(.+?)'", text)
    return m.group(1) if m else default


def measure_performance(func):
    async def wrapper(*args, **kwargs):
        start = perf_counter()
        ret = await func(*args, **kwargs)
        t = (perf_counter() - start) * 1000
        print(f"PERF: {func.__name__} took {t:.3f} ms")
        return ret

    return wrapper


T = TypeVar("T")


def get_first(iterable: Iterable[T], **attrs: Any) -> Optional[T]:
    if len(attrs) == 1:
        k, v = attrs.popitem()
        pred = attrgetter(k.replace("__", "."))
        for elem in iterable:
            if pred(elem) == v:
                return elem

        return None

    converted = [
        (attrgetter(attr.replace("__", ".")), value) for attr, value in attrs.items()
    ]

    for elem in iterable:
        if all(pred(elem) == value for pred, value in converted):
            return elem

    return None


@dataclass
class LoginInfo:
    type: LoginType
    prefix: str
    url: str = None  # set later
    # adfs cards
    vs: str = None
    vsg: str = None
    ev: str = None
    db: str = None


# wulkanowy sdk <3
logintype_selector = {
    LoginType.CUFS: ".loginButton, .LogOnBoard input[type=submit]",
    LoginType.ADFS: "#loginArea form#loginForm",
    LoginType.ADFSLight: ".submit-button",
    LoginType.ADFSCards: 'input[name="__VIEWSTATE"]',
}

re_login_prefix = re.compile(r"var userNameValue = '([A-Z]+?)\\\\' \+ userName\.value;")


def extract_login_info(text: str) -> LoginInfo:
    soup = BeautifulSoup(text, "lxml")

    type = LoginType.UNKNOWN
    for k in logintype_selector:
        if soup.select(logintype_selector[k]):
            type = k
            break

    m = re_login_prefix.search(text)
    prefix = m.group(1) if m else ""

    info = LoginInfo(type=type, prefix=prefix)
    if type is LoginType.ADFSCards:
        info.vs = soup.select('input[name="__VIEWSTATE"]')[0]["value"]
        info.vsg = soup.select('input[name="__VIEWSTATEGENERATOR"]')[0]["value"]
        info.ev = soup.select('input[name="__EVENTVALIDATION"]')[0]["value"]
        info.db = soup.select('input[name="__db"]')[0]["value"]

    return info
