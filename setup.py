#! /usr/bin/env python
from setuptools import setup, find_packages


def read(filename):
    with open(filename, "r", encoding="utf-8") as fp:
        return fp.read()


long_description = u'\n\n'.join(
    [
        read('README.rst'),
        read('AUTHORS.rst'),
        read('CHANGES.rst'),
    ]
)

setup(
    name="cruAKtemp",
    version="0.2.0.dev0",
    author="J Scott Stewart",
    author_email="james.stewart@colorado.edu",
    description="Python package for accessing CRU NCEP data temperature for Alaska",
    long_description=long_description,
    url="http://github.com/permamodel/cruAKtemp",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Scientific/Engineering :: Physics",
    ],
    keywords=["permamodel", "permafrost", "alaska", "data"],
    install_requires=open("requirements.txt", "r").read().splitlines(),
    setup_requires=[],
    packages=find_packages(),
    package_data={"": ["examples/*", "data/*"]},
    include_package_data=True,
)
