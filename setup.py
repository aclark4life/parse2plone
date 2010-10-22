
from setuptools import setup

name = 'parse2plone'
description = 'Easily import static HTML files into Plone.' 
version = '0.5'

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
        'Plone',
        'lxml',
        'BeautifulSoup',
    ],
    py_modules=['parse2plone'],
)
