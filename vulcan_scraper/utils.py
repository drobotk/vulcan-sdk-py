import re
from typing import *
from dataclasses import dataclass, is_dataclass
from time import perf_counter

from bs4 import BeautifulSoup, element
from .error import *

def extract_cert( text: str ) -> tuple[str, str, str]:
    try:
        soup = BeautifulSoup( text, 'lxml')
        wa = soup.select('input[name="wa"]')[0]['value']
        wctx = soup.select('input[name="wctx"]')[0]['value']
        wresult = soup.select('input[name="wresult"]')[0]['value']
    
    except Exception as e:
        raise ScraperException(f"Extracting cert failed: {type(e)}: {e}")

    else:
        return wa, wctx, wresult

def extract_symbols( wresult: str ) -> list[str]:
    try:
        soup = BeautifulSoup( wresult, "lxml-xml")
        tags = soup.select('[AttributeName="UserInstance"]')[0].children
        symbols = [ c.contents[0] for c in tags if type(c) == element.Tag ]
        symbols = [ s for s in symbols if ' ' not in s ] # filter out invalid symbols 
        
    except Exception as e:
        raise ScraperException(f"Extracting symbols failed: {type(e)}: {e}")

    else:
        return symbols

def extract_instances( text: str ) -> list[str]:
    try:
        soup = BeautifulSoup( text, "lxml")
        tags = soup.select('.panel.linkownia.pracownik.klient a[href*="uonetplus-uczen"]')
        links = [ a['href'] for a in tags ]
        instances = [ l.split("/")[4] for l in links ]
        
    except Exception as e:
        raise ScraperException(f"Extracting instances failed: {type(e)}: {e}")

    else:
        return instances

def get_script_param( text: str, param: str, default: str = None ) -> str:
    m = re.search(f"{param}: '.*'", text )
    return m.group()[ len( param )+3:-1 ] if m else default

def reprable( *attrs ):
    def wrapper( cls ):
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

def get_default( data: dict, key: str, default: Any ):
    return data.get( key, default ) or default

def measure_performance( func ):
    async def wrapper( *args, **kwargs ):
        start = perf_counter()
        ret = await func( *args, **kwargs )
        t = ( perf_counter() - start ) * 1000
        print(f"PERF: {func.__name__} took {t:.3f} ms")
        return ret
        
    return wrapper