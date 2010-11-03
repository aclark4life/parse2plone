
from setuptools import setup

name = 'parse2plone'
description = 'Easily import static HTML websites into Plone.' 
version = '0.9'

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
    url='http://aclark4life.github.com/Parse2Plone',
    author='Alex Clark',
    author_email='aclark@aclark.net',
    entry_points={
        'zc.buildout': ['default = %s:Recipe' % name],
    },
    install_requires=[
        'BeautifulSoup',
        'lxml',
        'zc.buildout',
    ],
    py_modules=['parse2plone','slugify','rename'],
    classifiers=[
        'Framework :: Buildout',
        'Framework :: Plone'
    ],
    extras_require={
        'tests': ['zope.testing'],
    },
)
