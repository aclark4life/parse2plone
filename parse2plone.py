# -*- coding: utf-8 -*-

###############################################################################
#                                                                             #
# Usage:                                                                      #
#                                                                             #
#     $ bin/plone run bin/import /path/to/files                               #
#                                                                             #
# See README.txt for more information                                         #
#                                                                             #
###############################################################################

"""Recipe parse2plone"""

import fnmatch
import logging

from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SpecialUsers import system
from Testing.makerequest import makerequest

from lxml.html import parse
from optparse import OptionParser
from os import path as os_path
from os import walk
from pkg_resources import working_set
from sys import argv, exc_info, executable
from transaction import commit
from zExceptions import BadRequest
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

            # http://goo.gl/qm3f
            # The value passed is a source string to be placed between the
            # parentheses in the call
            arguments='app')

        # Return files that were created by the recipe. The buildout
        # will remove all returned files upon reinstall.
        return tuple()

    def update(self):
        """Updater"""
        pass


line = """
===============================================================================
"""


class Parse2Plone(object):

    logger = logging.getLogger("parse2plone")
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    # "application" code
#    logger.debug("debug message")
#    logger.info("info message")
#    logger.warn("warn message")
#    logger.error("error message")
#    logger.critical("critical message")

    illegal_chars = ('_',)
    html_file_ext = ('html',)
    image_file_ext = ('gif', 'jpg', 'jpeg', 'png',)

    def path_to_list(self, file):
        return file.split('/')

    def list_to_path(self, file):
        return '/'.join(file)

    def pretty_print(self, obj):
        return self.list_to_path(obj.getPhysicalPath())

    def is_folder(self, obj):
        if len(obj.split('.')) == 1:
            return True
        else:
            return False

    def is_html(self, obj):
        result = False
        for ext in self.html_file_ext:
            if obj.endswith(ext):
                result = True
        return result

    def is_image(self, obj):
        result = False
        for ext in self.image_file_ext:
            if obj.endswith(ext):
                result = True
        return result

    def parse_options(self):
        parser = OptionParser()
        parser.add_option("-i", "--ignore", dest="ignore",
                          help="Number of dirs to ignore")
        return parser

    def check_exists(self, parent, obj):
        if obj in parent:
            return True
        else:
            return False

    def set_title(self, obj, title):
        obj.setTitle(title.title())
        obj.reindexObject()
        commit()

    def setup_app(self, app):
        app = makerequest(app)
        newSecurityManager(None, system)
        site = app.Plone
        return site

    def get_files(self, dir):
        results = []
        for path, subdirs, files in walk(dir):
            for file in fnmatch.filter(files, '*'):
                results.append(os_path.join(path, file))
        return results

    def ignore_parts(self, files, ignore):
        results = []
        for file in files:
            parts = self.path_to_list(file)
            if not ignore == '':
                parts = parts[int(ignore):]
            results.append(parts)
        return results

    def prep_files(self, files, ignore):
        results = []
        files = self.ignore_parts(files, ignore)
        for file in files:
            results.append(self.list_to_path(file))
        return results

    def get_parent(self, parent, prefix):
        if prefix is not '':
            newp = parent.restrictedTraverse(prefix)
            self.logger.info('update parent from %s to %s' % (
                self.pretty_print(parent), 
                self.pretty_print(newp)))
            return newp
        else:
            return parent

    def create_folder(self, parent, obj):
        self.logger.info( "creating folder '%s' inside parent folder '%s'" % (obj,
            self.pretty_print(parent)))
        parent.invokeFactory('Folder', obj)
        commit()
        return parent[obj]

    def create_page(self, parent, obj):
        self.logger.info( "creating page '%s' inside parent folder '%s'" % (obj,
            self.pretty_print(parent)))
        parent.invokeFactory('Document', obj)
        commit()
        return parent[obj]

    def create_image(self, parent, obj):
        self.logger.info( "creating image '%s' inside parent folder '%s'" % (obj,
            self.pretty_print(parent)))
        parent.invokeFactory('Image', obj)
        commit()
        return parent[obj]

    def create_content(self, parent, obj):
        if self.is_folder(obj):
            folder = self.create_folder(parent, obj)
            self.set_title(folder, obj)
        elif self.is_html(obj):
            page = self.create_page(parent, obj)
            self.set_title(page, obj)
        elif self.is_image(obj):
            image = self.create_image(parent, obj)
            self.set_title(image, obj)

    def add_files(self, site, files):
        count = 0
        for file in files:
            count += 1
            parts = self.path_to_list(file)
            parent = site
            for i in range(len(parts)):
                path = self.list_to_path(parts[:i + 1])
                prefix = self.path_to_list(path)[:-1]
                obj = self.path_to_list(path)[-1:][0]

                if obj[0] not in self.illegal_chars:
                    parent = self.get_parent(parent, self.list_to_path(prefix))
                    if self.check_exists(parent, obj):
                        self.logger.info( '%s exists inside %s' % (obj,
                            self.pretty_print(parent)))
                    else:
                        self.logger.info( '%s does not exist inside %s' % (obj,
                            self.pretty_print(parent)))
                        self.create_content(parent, obj)
                else:
                    break
        return 'Imported %s files' % count


def main(app):
    p2p = Parse2Plone()
    parser = p2p.parse_options()
    options, args = parser.parse_args()
    dir = argv[1]
    site = p2p.setup_app(app)
    files = p2p.get_files(dir)
    files = p2p.prep_files(files, options.ignore)
    results = p2p.add_files(site, files)
    print results
