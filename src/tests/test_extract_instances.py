from vulcan_scraper.utils import extract_instances, Instance


def test_extract_instances():
    with open("resources/uonetplus/start.html") as f:
        text = f.read()

    instances = extract_instances(text)

    assert instances == [
        Instance(id="123456", name="SZK1"),
        Instance(id="123457", name="SZK2"),
        Instance(id="123458", name=""),
    ]
