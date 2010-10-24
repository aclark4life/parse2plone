
from setuptools import setup

name = 'parse2plone'
description = 'Easily import static HTML files into Plone.' 
version = '0.6'

def read(file):
    file = open(file)
    data = file.read()
    file.close()
    return data

setup(
    name=name,
    version=version,
    description=description,
    long_description=read('README.txt')+read('docs/HISTORY.txt'),
    url='http://aclark4life.github.com/Parse-to-Plone',
    author='Alex Clark',
    author_email='aclark@aclark.net',
    entry_points={
        'zc.buildout': ['default = %s:Recipe' % name],
    },
    install_requires=[
        'lxml',
        'BeautifulSoup',
    ],
    py_modules=['parse2plone'],
    classifiers=[
        'Framework :: Buildout'
        'Framework :: Plone'
    ],
    extras_require={
        'tests': ['zope.testing'],
    }
)
