
from setuptools import setup

name = 'parse2plone'
version='0.1'

setup(
    name=name,
    version=version,
    entry_points={
        'zc.buildout': ['default = %s:Recipe' % name],
    },
    install_requires=[
        'lxml',
        'BeautifulSoup',
    ],
    packages = [
        '.',
    ]
)
