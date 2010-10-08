
from setuptools import setup

setup(
    name = 'parse2plone',
    entry_points = {
        'console_scripts': [
            'import = parse2plone:main',
        ],
    },
    install_requires = [
        'lxml',
        'BeautifulSoup',
    ],
)
