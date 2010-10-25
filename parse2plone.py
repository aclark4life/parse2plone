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

from copy import deepcopy
from lxml.html import fromstring
from optparse import OptionParser
from os import path as os_path
from os import walk
from pkg_resources import working_set
from sys import executable
from transaction import commit
from zc.buildout.easy_install import scripts as create_scripts


defaults = {
    'path': ['/Plone/burmese'],
    'illegal_chars': ['_', '.'],
    'html_extensions': ['html'],
    'image_extensions': ['gif', 'jpg', 'jpeg', 'png'],
    'target_tags': ['a', 'div', 'h1', 'h2', 'p'],
}


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


class Utils(object):

    def split_input(self, input, delimiter):
        return input.split(delimiter)

    def join_input(self, input, delimiter):
        return delimiter.join(input)

    def pretty_print(self, obj):
        return self.join_input(obj.getPhysicalPath(), '/')

    def is_folder(self, obj):
        if len(obj.split('.')) == 1:
            return True
        else:
            return False

    def is_html(self, obj, html_extensions):
        result = False
        for ext in html_extensions:
            if obj.endswith(ext):
                result = True
        return result

    def is_image(self, obj, image_extensions):
        result = False
        for ext in image_extensions:
            if obj.endswith(ext):
                result = True
        return result

    def is_path(self, app, path):
        if path.startswith('/'):
            path = path[1:]
        if len(path.split('/')) > 1:
            site = app.restrictedTraverse(path)
        else:
            site = app[path]
        return site

    def check_exists(self, parent, obj):
        if obj in parent:
            return True
        else:
            return False

    def create_option_parser(self):
        option_parser = OptionParser()
        option_parser.add_option("-p", "--path", dest="path",
            help="Path to Plone site object")
        option_parser.add_option("", "--html-extensions",
            dest="html_extensions", help="Specify HTML file extensions")
        option_parser.add_option("", "--illegal-chars", dest="illegal_chars",
            help="Specify characters to ignore")
        option_parser.add_option("", "--image-extensions",
            dest="image_extensions", help="Specify image file extensions")
        option_parser.add_option("", "--target-tags", dest="target_tags",
            help="Specify HTML tags to parse")
        return option_parser


class Parse2Plone(object):
    utils = Utils()
    logger = setup_logger()

    def set_title(self, obj, title):
        obj.setTitle(title.title())
        obj.reindexObject()
        commit()

    def setup_app(self, app, path):
        app = makerequest(app)
        newSecurityManager(None, system)
        if path is not '':
            try:
                site = self.utils.is_path(app, path)
            except KeyError:
                self.logger.error("site object '%s' does not exist" % path)
                exit(1)
        else:
            site = app.Plone
        return site

    def get_files(self, import_dir):
        results = []
        for path, subdirs, files in walk(import_dir):
            for file in fnmatch.filter(files, '*'):
                results.append(os_path.join(path, file))
        return results

    def ignore_parts(self, files, ignore):
        results = []
        for file in files:
            parts = self.utils.split_input(file, '/')
            if ignore is not '':
                parts = parts[ignore:]
            results.append(parts)
        return results

    def prep_files(self, files, ignore):
        base = self.utils.join_input(
            self.utils.split_input(files[0], '/')[:ignore], '/')
        results = {base: []}
        files = self.ignore_parts(files, ignore)
        for file in files:
            results[base].append(self.utils.join_input(file, '/'))
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
        file = open('/'.join([base, self.utils.join_input(prefix, '/'), obj]),
            'rb')
        data = file.read()
        file.close()
        image.setImage(data)
        commit()

    def set_page(self, page, obj, base, prefix, target_tags):
        results = ''
        file = open('/'.join([base, self.utils.join_input(prefix, '/'), obj]),
            'rb')
        data = file.read()
        file.close()
        root = fromstring(data)
        for element in root.iter():
            tag = element.tag
            text = element.text
            if tag in target_tags and text is not None:
                results += '<%s>%s</%s>' % (tag, text, tag)
        page.setText(results)
        commit()

    def create_content(self,
        parent,
        obj,
        count,
        base,
        prefix,
        html_extensions,
        image_extensions,
        target_tags):
        if self.utils.is_folder(obj):
            folder = self.create_folder(parent, obj)
            self.set_title(folder, obj)
            count['folders'] += 1
        elif self.utils.is_html(obj, html_extensions):
            page = self.create_page(parent, obj)
            self.set_title(page, obj)
            self.set_page(page, obj, base, prefix, target_tags)
            count['pages'] += 1
        elif self.utils.is_image(obj, image_extensions):
            image = self.create_image(parent, obj)
            self.set_title(image, obj)
            self.set_image(image, obj, base, prefix)
            count['images'] += 1
        return count

    def import_files(self, site, files, illegal_chars, html_extensions,
        image_extensions, target_tags):
        count = {'folders': 0, 'pages': 0, 'images': 0}
        base = files.keys()[0]
        for file in files[base]:
            parts = self.utils.split_input(file, '/')
            parent = site
            for i in range(len(parts)):
                path = self.utils.join_input(parts[:i + 1], '/')
                prefix = self.utils.split_input(path, '/')[:-1]
                obj = self.utils.split_input(path, '/')[-1:][0]
                if obj[0] not in illegal_chars:
                    parent = self.get_parent(parent,
                        self.utils.join_input(prefix, '/'))
                    if self.utils.check_exists(parent, obj):
                        self.logger.info("object '%s' exists inside '%s'" % (
                            obj, self.utils.pretty_print(parent)))
                    else:
                        self.logger.info(
                            "object '%s' does not exist inside '%s'"
                            % (obj, self.utils.pretty_print(parent)))
                        count = self.create_content(
                                parent,
                                obj,
                                count,
                                base,
                                prefix,
                                html_extensions,
                                image_extensions,
                                target_tags)
                else:
                    break
        self.logger.info('Imported %s folders, %s pages, and %s images.' %
           tuple(count.values()))


class Recipe(object):
    """zc.buildout recipe"""

    utils = Utils()

    def __init__(self, buildout, name, options):
        self.buildout, self.name, self.options = buildout, name, options

    def install(self):
        """Installer"""
        bindir = self.buildout['buildout']['bin-directory']

        path, illegal_chars, html_extensions, image_extensions, target_tags = (
            self.parse_options(self.options))

        arguments = "app, path='%s', illegal_chars='%s', html_extensions='%s',"
        arguments += " image_extensions='%s', target_tags='%s'"

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
            arguments=arguments % (path, illegal_chars, html_extensions,
                image_extensions, target_tags))
        return tuple()

    def update(self):
        """Updater"""
        pass

    def parse_options(self, options):
        results = deepcopy(defaults)
        join_input = self.utils.join_input
        split_input = self.utils.split_input
        for option in results:
            results[option] = None
        for option in results:
            if option in options:
                results[option] = join_input(options[option], ',')
            else:
                results[option] = join_input(defaults[option], ',')

        path, target_tags, html_extensions, image_extensions, illegal_chars = (
            results.values())
        return (path, illegal_chars, html_extensions, image_extensions,
            target_tags)


def main(app, path=None, illegal_chars=None, html_extensions=None,
    image_extensions=None, target_tags=None):
    """parse2plone"""

    # Process args
    utils = Utils()

    illegal_chars = utils.split_input(illegal_chars, ',')
    html_extensions = utils.split_input(html_extensions, ',')
    image_extensions = utils.split_input(image_extensions, ',')
    target_tags = utils.split_input(target_tags, ',')

    option_parser = utils.create_option_parser()
    options, args = option_parser.parse_args()

    # Configure settings
    import_dir = args[0]
    ignore = len(utils.split_input(import_dir, '/'))
    if options.path is not None:
        path = options.path

    # Run parse2plone
    parse2plone = Parse2Plone()
    site = parse2plone.setup_app(app, path)
    files = parse2plone.get_files(import_dir)
    files = parse2plone.prep_files(files, ignore)
    parse2plone.import_files(site, files, illegal_chars, html_extensions,
        image_extensions, target_tags)
