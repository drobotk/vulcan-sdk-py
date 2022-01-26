from vulcan_scraper.model import CertificateResponse
from vulcan_scraper.utils import extract_symbols


def test_parse_cert():
    with open("resources/cufs/certresponse.html") as f:
        text = f.read()

    cres = CertificateResponse(text)

    assert cres.wa == "wsignin1.0"
    assert cres.wresult
    assert cres.wctx == "http://uonetplus.fakelog.cf/Default/LoginEndpoint.aspx"

    symbols = extract_symbols(cres.wresult)

    assert symbols == ["Default", "powiatwulkanowy", "warszawa", "asdf", "asdfsdf"]
