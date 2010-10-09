# -*- coding: utf-8 -*-
"""Recipe parse2plone"""

import fnmatch

from lxml.html import parse
from os import path, walk
from pkg_resources import working_set
from sys import argv, executable
from zc.buildout.easy_install import scripts as create_scripts


class Recipe(object):
    """zc.buildout recipe"""

    def __init__(self, buildout, name, options):
        self.buildout, self.name, self.options = buildout, name, options

    def install(self):
        """Installer"""

        bindir = self.buildout['buildout']['bin-directory']

        create_scripts(

            # http://pypi.python.org/pypi/zc.buildout#the-scripts-function
            # A sequence of distribution requirements.
            [('import', 'parse2plone', 'main')],

            # A working set,
            working_set,

            # The Python executable to use,
            executable,

            # The destination directory.
            bindir,

            # http://pypi.python.org/pypi/zc.buildout#the-scripts-function-providing-script-arguments
            # The value passed is a source string to be placed between the parentheses in the call
            arguments='app')

        # Return files that were created by the recipe. The buildout
        # will remove all returned files upon reinstall.
        return tuple()

    def update(self):
        """Updater"""
        pass


def main(app):
    dir = argv[1]
    htmlfiles = []
    for fspath, subdirs, files in walk(dir):
        for file in fnmatch.filter(files, '*.html'):
            htmlfiles.append(path.join(fspath, file))

    for file in htmlfiles:
        obj = parse(file) 
        for element in obj.iter():
            print element
