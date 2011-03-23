import os

from setuptools import setup, find_packages

name = 'charm'
description = 'Import static websites on the file system into Plone.'
version = '1.0b4'


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
    data_files=[
        ('html/2011/01/01/test-collapse', ['html/2011/01/01/test-collapse/index.html']),
        ('html/_sample', ['html/_sample/index.html']),
        ('html/a', ['html/a/index.html']),
        ('html/ac', ['html/ac/index.html']),
        ('html/condimentum', ['html/condimentum/index.html']),
        ('html/cursus', ['html/cursus/index.html']),
        ('html/dis', ['html/dis/index.html']),
        ('html/fames', ['html/fames/index.html']),
        ('html/gravida', ['html/gravida/index.html']),
        ('html/id', ['html/id/index.html']),
        ('html', ['html/index.html']),
        ('html/integer', ['html/integer/index.html']),
        ('html/libero', ['html/libero/index.html']),
        ('html/mi', ['html/mi/index.html']),
        ('html/mollis', ['html/mollis/index.html']),
        ('html/nec', ['html/nec/index.html']),
        ('html/nulla', ['html/nulla/index.html']),
        ('html/nullam', ['html/nullam/index.html']),
        ('html/pede', ['html/pede/index.html']),
        ('html/phasellus', ['html/phasellus/index.html']),
        ('html/platea', ['html/platea/index.html']),
        ('html', ['html/plone-logo-128-white-bg.png']),
        ('html/porta', ['html/porta/index.html']),
        ('html', ['html/README.txt']),
        ('html/risus', ['html/risus/index.html']),
        ('html', ['html/sample.doc']),
        ('html', ['html/sample.xls'])
    ],
    packages = find_packages('.'),  # include all packages under src
    package_dir = {'':'.'},   # tell distutils packages are under src
)
