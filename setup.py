# encoding: utf-8

from setuptools import setup, find_packages

name = 'parse2plone'
description = 'Easily import static HTML files into Plone.' 
version = '0.1'

def read(file):
    file = open(file)
    data = file.read()
    file.close()
    return data

setup(
    name=name,
    version=version,
    description=description,
    long_description=read('README.txt'),
    entry_points={
        'zc.buildout': ['default = %s:Recipe' % name],
    },
    install_requires=[
        'lxml',
        'BeautifulSoup',
    ],
    packages=find_packages(),
)
