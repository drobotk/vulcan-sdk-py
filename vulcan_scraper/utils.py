import re
from dataclasses import dataclass, is_dataclass
from operator import attrgetter
from time import perf_counter
from typing import *

from bs4 import BeautifulSoup

from .enum import LoginType
from .error import *

re_valid_symbol = re.compile(r"[a-zA-Z0-9]*")


def extract_cert(text: str) -> tuple[str, str, str, str]:
    try:
        soup = BeautifulSoup(text, "lxml")
        wa = soup.select('input[name="wa"]')[0]["value"]
        wctx = soup.select('input[name="wctx"]')[0]["value"]
        wresult = soup.select('input[name="wresult"]')[0]["value"]
        action = soup.select("form")[0]["action"]

    except Exception as e:
        raise ScraperException(f"Extracting cert failed: {type(e)}: {e}")

    else:
        return wa, wctx, wresult, action


def extract_symbols(wresult: str) -> list[str]:
    try:
        soup = BeautifulSoup(wresult.replace(":", ""), "lxml")
        tags = soup.select(
            'samlAttribute[AttributeName$="Instance"] samlAttributeValue'
        )
        symbols = [tag.text.strip() for tag in tags]
        symbols = [s for s in symbols if re_valid_symbol.fullmatch(s)]

    except Exception as e:
        raise ScraperException(f"Extracting symbols failed: {type(e)}: {e}")

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
        raise ScraperException(f"Extracting instances failed: {type(e)}: {e}")

    else:
        return instances


def get_script_param(text: str, param: str, default: str = None) -> str:
    m = re.search(f"{param}: '(.+?)'", text)
    return m.group(1) if m else default


def reprable(*attrs):
    def wrapper(cls):
        def __repr__(self) -> str:
            return f'<{self.__class__.__name__} { " ".join([ f"{attr}={repr(getattr(self, attr))}" for attr in attrs ]) }>'

        cls.__repr__ = __repr__

        return cls

    return wrapper


def nested_dataclass(*args, **kwargs):
    def wrapper(cls):
        cls = dataclass(cls, **kwargs)
        original_init = cls.__init__

        def __init__(self, *args, **kwargs):
            for name, value in kwargs.items():
                field_type = cls.__annotations__.get(name, None)
                if is_dataclass(field_type) and isinstance(value, dict):
                    new_obj = field_type(**value)
                    kwargs[name] = new_obj
            original_init(self, *args, **kwargs)

        cls.__init__ = __init__
        return cls

    return wrapper(args[0]) if args else wrapper


def get_default(data: dict, key: str, default: Any):
    return data.get(key, default) or default


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


# wulkanowy sdk <3
logintype_selector = {
    LoginType.CUFS: ".loginButton, .LogOnBoard input[type=submit]",
    LoginType.ADFS: "#loginArea form#loginForm",
    LoginType.ADFSLight: ".submit-button",
    LoginType.ADFSLightCards: "#__VIEWSTATE",
}

re_login_prefix = re.compile(r"var userNameValue = '(.+?)' \+ userName\.value;")


def extract_login_info(text: str) -> LoginInfo:
    soup = BeautifulSoup(text, "lxml")

    type = LoginType.UNKNOWN
    for k in logintype_selector:
        if soup.select(logintype_selector[k]):
            type = k
            break

    m = re_login_prefix.search(text)
    prefix = m.group(1) if m else ""

    return LoginInfo(type=type, prefix=prefix)
