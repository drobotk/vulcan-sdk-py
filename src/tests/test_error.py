from pytest import raises
from vulcan_scraper.utils import check_for_vulcan_error
from vulcan_scraper.error import (
    BadCredentialsException,
    InvalidSymbolException,
    ServiceUnavailableException,
    VulcanException,
)


def check(filename: str, error: type):
    with open(filename) as f:
        text = f.read()

    with raises(error):
        check_for_vulcan_error(text)


def test_credentials():
    check("resources/error/credentials.html", BadCredentialsException)


def test_symbol():
    check("resources/error/symbol.html", InvalidSymbolException)


def test_database():
    check("resources/error/baza.html", ServiceUnavailableException)


def test_unexpected():
    check("resources/error/nieoczekiwany.html", VulcanException)
