
from setuptools import setup, find_packages

name = 'mr.importer'
description = 'Easily import static websites on the file system into Plone'
version = '1.0a6'


def read(file):
    file = open(file)
    data = file.read()
    file.close()
    return data

setup(
    name=name,
    version=version,
    description=description,
    long_description=read('README.txt') + read('docs/HISTORY.txt'),
    url='https://github.com/collective/mr.importer',
    author='Alex Clark',
    author_email='aclark@aclark.net',
    entry_points={
        'zc.buildout': ['default = %s:Recipe' % name],
    },
    install_requires=[
        'BeautifulSoup',
        'lxml',
        'xlrd',
        'zc.buildout',
    ],
    packages=find_packages(),
    classifiers=[
        'Framework :: Buildout',
        'Framework :: Plone'
    ],
    extras_require={
        'tests': ['zope.testing', 'Plone'],
    },
)
