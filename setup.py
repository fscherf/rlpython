#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

from rlpython import VERSION_STRING

setup(
    include_package_data=False,
    name='rlpython',
    version=VERSION_STRING,
    author='Florian Scherf',
    url='https://github.com/fscherf/rlpython',
    author_email='f.scherf@pengutronix.de',
    license='MIT',
    packages=find_packages(),
    install_requires=[],
    scripts=[
        'bin/rlpython',
    ],
)
