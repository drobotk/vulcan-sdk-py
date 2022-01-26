from setuptools import setup
from re import search


NAME = "vulcan-sdk-py"
PACKAGE = "vulcan_scraper"
SRC_DIR = "src"


def install():
    with open(f"{SRC_DIR}/{PACKAGE}/__init__.py") as f:
        text = f.read()
        version = search('__version__ = "(.+?)"', text).group(1)
        author = search('__author__ = "(.+?)"', text).group(1)

    with open("requirements.txt") as f:
        requirements = f.read().splitlines()

    setup(
        name=NAME,
        version=version,
        author=author,
        packages=[PACKAGE],
        package_dir={"": SRC_DIR},
        install_requires=requirements,
    )


if __name__ == "__main__":
    install()
