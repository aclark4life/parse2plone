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


def setup_logger():
    # log levels: debug, info, warn, error, critical
    logger = logging.getLogger("parse2plone")
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


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
        return tuple()

    def update(self):
        """Updater"""
        pass


class Utils(object):
    illegal_chars = ('_',)
    html_file_ext = ('html',)
    image_file_ext = ('gif', 'jpg', 'jpeg', 'png',)

    def string_to_list(self, file):
        return file.split('/')

    def list_to_string(self, file):
        return '/'.join(file)

    def pretty_print(self, obj):
        return self.list_to_string(obj.getPhysicalPath())

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

    def check_exists(self, parent, obj):
        if obj in parent:
            return True
        else:
            return False


class Parse2Plone(object):
    utils = Utils()
    logger = setup_logger()

    def parse_options(self):
        parser = OptionParser()
        return parser

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
            parts = self.utils.string_to_list(file)
            if not ignore == '':
                parts = parts[ignore:]
            results.append(parts)
        return results

    def prep_files(self, files, ignore):
        base = self.utils.list_to_string(
            self.utils.string_to_list(files[0])[:ignore])
        results = {base: []}
        files = self.ignore_parts(files, ignore)
        for file in files:
            results[base].append(self.utils.list_to_string(file))
        return results

    def get_parent(self, parent, prefix):
        if prefix is not '':
            newp = parent.restrictedTraverse(prefix)
            self.logger.info('updating parent from %s to %s' % (
                self.utils.pretty_print(parent),
                self.utils.pretty_print(newp)))
            return newp
        else:
            return parent

    def create_folder(self, parent, obj):
        self.logger.info("creating folder '%s' inside parent folder '%s'" % (
            obj, self.utils.pretty_print(parent)))
        parent.invokeFactory('Folder', obj)
        commit()
        return parent[obj]

    def create_page(self, parent, obj):
        self.logger.info("creating page '%s' inside parent folder '%s'" % (obj,
            self.utils.pretty_print(parent)))
        parent.invokeFactory('Document', obj)
        commit()
        return parent[obj]

    def create_image(self, parent, obj):
        self.logger.info("creating image '%s' inside parent folder '%s'" % (
            obj, self.utils.pretty_print(parent)))
        parent.invokeFactory('Image', obj)
        commit()
        return parent[obj]

    def set_image(self, image, obj, base, prefix):
        file = open('/'.join([base, self.utils.list_to_string(prefix), obj]),
            'rb')
        data = file.read()
        file.close()
        image.setImage(data)

    def create_content(self, parent, obj, count, base, prefix):
        if self.utils.is_folder(obj):
            folder = self.create_folder(parent, obj)
            self.set_title(folder, obj)
            count['folders'] += 1
        elif self.utils.is_html(obj):
            page = self.create_page(parent, obj)
            self.set_title(page, obj)
            count['pages'] += 1
        elif self.utils.is_image(obj):
            image = self.create_image(parent, obj)
            self.set_title(image, obj)
            self.set_image(image, obj, base, prefix)
            count['images'] += 1
        return count

    def add_files(self, site, files):
        count = {'folders': 0, 'pages': 0, 'images': 0}
        base = files.keys()[0]
        for file in files[base]:
            parts = self.utils.string_to_list(file)
            parent = site
            for i in range(len(parts)):
                path = self.utils.list_to_string(parts[:i + 1])
                prefix = self.utils.string_to_list(path)[:-1]
                obj = self.utils.string_to_list(path)[-1:][0]
                if obj[0] not in self.utils.illegal_chars:
                    parent = self.get_parent(parent,
                        self.utils.list_to_string(prefix))
                    if self.utils.check_exists(parent, obj):
                        self.logger.info("object '%s' exists inside '%s'" % (
                            obj, self.utils.pretty_print(parent)))
                    else:
                        self.logger.info(
                            "object '%s' does not exist inside '%s'"
                            % (obj, self.utils.pretty_print(parent)))
                        count = self.create_content(parent, obj, count, base,
                            prefix)
                else:
                    break
        self.logger.info('Imported %s folders, %s pages, and %s images.' %
           tuple(count.values()))


def main(app):
    p2p = Parse2Plone()
    utils = Utils()
    parser = p2p.parse_options()
    options, args = parser.parse_args()
    dir = argv[1]
    ignore = len(utils.string_to_list(dir))
    site = p2p.setup_app(app)
    files = p2p.get_files(dir)
    files = p2p.prep_files(files, ignore)
    p2p.add_files(site, files)
