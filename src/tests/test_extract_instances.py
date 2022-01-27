from vulcan_scraper.utils import extract_instances


def test_extract_instances():
    with open("resources/uonetplus/start.html") as f:
        text = f.read()

    instances = extract_instances(text)

    assert instances == ["123456", "123457", "123458"]
