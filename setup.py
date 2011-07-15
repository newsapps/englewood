#!/usr/bin/env python

from setuptools import setup

setup(
    name='englewood',
    version='0.0.1',
    description='Tools for deriving different types of maps from shapefiles.',
    long_description=open('README.rst').read(),
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
