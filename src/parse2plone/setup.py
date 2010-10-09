
from setuptools import setup

name = 'parse2plone'

setup(
    name=name,
    entry_points={
        'zc.buildout': ['default = %s:Recipe' % name],
    },
    install_requires=[
        'lxml',
        'BeautifulSoup',
    ],
)
