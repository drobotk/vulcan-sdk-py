from vulcan_scraper.enum import LoginType
from vulcan_scraper.utils import LoginInfo, extract_login_info


def check(filename: str, ltype: LoginType, prefix: str) -> LoginInfo:
    with open(filename) as f:
        text = f.read()

    info = extract_login_info(text)

    assert info.type == ltype
    assert info.prefix == prefix

    return info


def test_cufs():
    check("resources/login/cufs.html", LoginType.CUFS, "")


def test_adfs():
    check("resources/login/adfs.html", LoginType.ADFS, "EDUNET")


def test_adfslight():
    check("resources/login/adfslight.html", LoginType.ADFSLight, "")


def test_adfscards():
    info = check("resources/login/adfscards.html", LoginType.ADFSCards, "")
    assert info.vs and info.vsg and info.ev and info.db
