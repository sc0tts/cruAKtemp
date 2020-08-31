#! /usr/bin/env python
from setuptools import setup, find_packages


setup(
    name="cruAKtemp",
    version="0.1.0",
    author="J Scott Stewart",
    author_email="james.stewart@colorado.edu",
    description="Python package for accessing CRU NCEP data temperature for Alaska",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="http://github.com/permamodel/cruAKtemp",
    classifiers=[
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
