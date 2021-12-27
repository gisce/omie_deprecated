# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

PACKAGES_DATA = {'omie': ['data/*.xsd']}

setup(
    name='omie',
    version='1.0',
    packages=find_packages(),
    url='https://github.com/gisce/omie',
    license='MIT',
    install_requires=['libsaas'],
    author='GISCE-TI, S.L.',
    author_email='devel@gisce.net',
    description='Interacts with OMIE API',
    package_data=PACKAGES_DATA,
)
