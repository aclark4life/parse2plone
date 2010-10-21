
from setuptools import setup

name = 'parse2plone'
version = '0.1'

def read(file):
    file = open(file)
    data = file.read()
    file.close()
    return data

setup(
    name=name,
    version=version,
    long_description=read('README.txt'),
    entry_points={
        'zc.buildout': ['default = %s:Recipe' % name],
    },
    install_requires=[
        'lxml',
        'BeautifulSoup',
    ],
)
