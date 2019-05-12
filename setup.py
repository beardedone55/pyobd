#!/usr/bin/env python3
# vim: shiftwidth=4:tabstop=4:expandtab
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pyobd-beardedone55",
    version="0.0.1",
    author="Brian LePage",
    author_email="bjlepage22@gmail.com",
    description="An automotive diagnostic tool for OBDII",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/beardedone55/pyobd",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: GPLv2",
        "Operating System :: OS Independent",
    ],
)
