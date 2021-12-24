# coding=utf8
from setuptools import setup, find_packages


setup(
    name="codegex",
    version="0.1.0",
    packages=find_packages(exclude=["tests"]),
    description="A regex-based code review tool for PRs",
    author="Anonymous",
    author_email="anonymous@example.com",
    license="LGPL",

    install_requires=[
        'loguru == 0.5.1', 'pytest == 6.0.1', 'regex == 2020.7.14', 'requests == 2.24.0', 'cachetools == 4.2.0'],
)

# to generate tar.gz file: python setup.py sdist
