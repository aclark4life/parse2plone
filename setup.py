import os

from setuptools import setup, find_packages

name = 'charm'
description = 'Import static websites on the file system into Plone.'
version = '1.0b3'


def read(file):
    file = open(file)
    data = file.read()
    file.close()
    return data

setup(
    name=name,
    version=version,
    description=description,
    long_description=read('README.txt') + read('docs/CONTRIBUTORS.txt') + read('docs/HISTORY.txt'),
    url='https://github.com/aclark4life/charm',
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
    py_modules=['charm'],
    classifiers=[
        'Framework :: Buildout',
        'Framework :: Plone'
    ],
    extras_require={
        'tests': ['zope.testing', 'Plone'],
    },
    data_files=[('html/2011/01/01/test-collapse', ['html/2011/01/01/test-collapse/index.html'])]
)
