#!/usr/bin/env python

import os
from setuptools import setup

def readme(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='englewood',
    version='0.0.4',
    description='Tools for deriving different types of maps from shapefiles.',
    long_description=readme('README.rst'),
    author='Christopher Groskopf',
    author_email='staringmonkey@gmail.com',
    url='http://blog.apps.chicagotribune.com/',
    license='MIT',
    packages=[
        'englewood', 
    ],
    install_requires = [
        'GDAL==1.6.0',
        ]
)
