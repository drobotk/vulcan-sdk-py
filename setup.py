from setuptools import setup, find_packages

VERSION = "0.1.2"

setup(
    name="vulcan-sdk-py",
    version=VERSION,
    maintainer="drobotk",
    packages=find_packages(),
    install_requires=open("requirements.txt").read().split("\n"),
)
