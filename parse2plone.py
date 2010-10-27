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

from ast import literal_eval
from copy import deepcopy
from lxml.html import fromstring
from optparse import OptionParser
from os import path as os_path
from os import walk
from pkg_resources import working_set
from sys import exc_info, executable
from transaction import commit
from zc.buildout.easy_install import scripts as create_scripts


defaults = {
    'path': ['/Plone'],
    'illegal_chars': ['_', '.'],
    'html_extensions': ['html'],
    'image_extensions': ['gif', 'jpg', 'jpeg', 'png'],
    'target_tags': ['a', 'div', 'h1', 'h2', 'p'],
    'force': ['False'],
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

    def check_exists_obj(self, parent, obj):
        if obj in parent:
            return True
        else:
            return False

    def check_exists_path(self, parent, path):
        try:
            parent.restrictedTraverse(path)
            return True
        except:
            return False

    def clean_path(self, path):
        if path.startswith('/'):
            return path[1:]

    def clean_recipe_input(self, illegal_chars, html_extensions,
        image_extensions, target_tags, path, force):

        illegal_chars = self.split_input(illegal_chars, ',')
        html_extensions = self.split_input(html_extensions, ',')
        image_extensions = self.split_input(image_extensions, ',')
        target_tags = self.split_input(target_tags, ',')
        path = self.clean_path(path)
        force = literal_eval(force)

        return (illegal_chars, html_extensions, image_extensions,
            target_tags, path, force)

    def create_option_parser(self):
        option_parser = OptionParser()
        option_parser.add_option("-p", "--path", dest="path",
            help="Path to Plone site object or sub-folder")
        option_parser.add_option("", "--html-extensions",
            dest="html_extensions", help="Specify HTML file extensions")
        option_parser.add_option("", "--illegal-chars", dest="illegal_chars",
            help="Specify characters to ignore")
        option_parser.add_option("", "--image-extensions",
            dest="image_extensions", help="Specify image file extensions")
        option_parser.add_option("", "--target-tags", dest="target_tags",
            help="Specify HTML tags to parse")
        option_parser.add_option("-f", "--force",
            action="store_true", dest="force", default=False,
            help="Force creation of folders")
        return option_parser

    def convert_recipe_options(self, options):
        """
        Convert recipe options into csv
        """
        results = deepcopy(defaults)
        join_input = self.join_input
        split_input = self.split_input
        for option in results:
            results[option] = None
        for option in results:
            if option in options:
                results[option] = join_input(options[option], ',')
            else:
                results[option] = join_input(defaults[option], ',')
        return results.values()

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

    def is_legal(self, obj, illegal_chars):
        if not obj[0] in illegal_chars:
            return True
        else:
            return False

    def join_input(self, input, delimiter):
        return delimiter.join(input)

    def obj_to_path(self, obj):
        return self.join_input(obj.getPhysicalPath(), '/')

    def process_command_line_args(self, options, illegal_chars,
        html_extensions, image_extensions, target_tags, path, force):
        if options.illegal_chars is not None:
            illegal_chars = options.illegal_chars
        if options.html_extensions is not None:
            html_extensions = options.html_extensions
        if options.image_extensions is not None:
            image_extensions = options.image_extensions
        if options.target_tags is not None:
            target_tags = options.target_tags
        if options.path is not None:
            path = options.path
        path = self.clean_path(path)
        if options.force is not None:
            force = options.force
        return (illegal_chars, html_extensions, image_extensions,
            target_tags, path, force)

    def setup_attrs(self, parse2plone, utils, count, illegal_chars,
        html_extensions, image_extensions, target_tags, logger):
        parse2plone.utils = utils
        parse2plone.count = count
        parse2plone.html_extensions = html_extensions
        parse2plone.image_extensions = image_extensions
        parse2plone.illegal_chars = illegal_chars
        parse2plone.target_tags = target_tags
        parse2plone.logger = logger
        return parse2plone

    def split_input(self, input, delimiter):
        return input.split(delimiter)


class Parse2Plone(object):

    def create_content(self, parent, obj, prefix_path, base):
        if self.utils.is_folder(obj):
            folder = self.create_folder(parent, obj)
            self.set_title(folder, obj)
            self.count['folders'] += 1
        elif self.utils.is_html(obj, self.html_extensions):
            page = self.create_page(parent, obj)
            self.set_title(page, obj)
            self.set_page(page, obj, prefix_path)
            self.count['pages'] += 1
        elif self.utils.is_image(obj, self.image_extensions):
            image = self.create_image(parent, obj)
            self.set_title(image, obj)
            self.set_image(image, obj, prefix_path, base)
            self.count['images'] += 1

    def create_folder(self, parent, obj):
        self.logger.info("creating folder '%s' inside parent folder '%s'" % (
            obj, self.utils.obj_to_path(parent)))
        parent.invokeFactory('Folder', obj)
        commit()
        return parent[obj]

    def create_image(self, parent, obj):
        self.logger.info("creating image '%s' inside parent folder '%s'" % (
            obj, self.utils.obj_to_path(parent)))
        parent.invokeFactory('Image', obj)
        commit()
        return parent[obj]

    def create_page(self, parent, obj):
        self.logger.info("creating page '%s' inside parent folder '%s'" % (obj,
            self.utils.obj_to_path(parent)))
        parent.invokeFactory('Document', obj)
        commit()
        return parent[obj]

    def create_parts(self, parent, parts, base):
        self.logger.info("creating parts for '%s'" % self.utils.join_input(
            parts, '/'))
        for i in range(len(parts)):
            path = self.get_path(parts, i)
            prefix_path = self.get_prefix_path(path)
            obj = self.get_obj(path)
            parent = self.get_parent(parent,
                self.utils.join_input(prefix_path, '/'))
            if self.utils.is_legal(obj, self.illegal_chars):
                if self.utils.check_exists_obj(parent, obj):
                    self.logger.info("object '%s' exists inside '%s'" % (
                        obj, self.utils.obj_to_path(parent)))
                else:
                    self.logger.info(
                        "object '%s' does not exist inside '%s'"
                        % (obj, self.utils.obj_to_path(parent)))
                    self.create_content(parent, obj, prefix_path, base)
            else:
                self.logger.info("object '%s' has illegal chars" % obj)
                break

    def get_base(self, files, ignore):
        return self.utils.join_input(self.utils.split_input(
            files[0], '/')[:ignore], '/')

    def get_files(self, import_dir):
        results = []
        for path, subdirs, files in walk(import_dir):
            self.logger.info("path '%s', has subdirs '%s', and files '%s'" % (
                path, self.utils.join_input(subdirs, ' '),
                self.utils.join_input(files, ' ')))
            for f in fnmatch.filter(files, '*'):
                if self.utils.is_legal(f, self.illegal_chars):
                    results.append(os_path.join(path, f))
                else:
                    self.logger.info("object '%s' has illegal chars" % f)
        return results

    def get_obj(self, path):
        return self.utils.split_input(path, '/')[-1:][0]

    def get_parent(self, current_parent, prefix_path):
        updated_parent = current_parent.restrictedTraverse(prefix_path)
        self.logger.info("updating parent from '%s' to '%s'" % (
             self.utils.obj_to_path(current_parent),
             self.utils.obj_to_path(updated_parent)))
        return updated_parent

    def get_parts(self, path):
        return self.utils.split_input(path, '/')

    def get_path(self, parts, i):
        return self.utils.join_input(parts[:i + 1], '/')

    def get_prefix_path(self, path):
        return self.utils.split_input(path, '/')[:-1]

    def ignore_parts(self, files, ignore):
        results = []
        for f in files:
            parts = self.get_parts(f)
            if ignore is not '':
                parts = parts[ignore:]
            results.append(parts)
        return results

    def import_files(self, parent, files, base):
        base = files.keys()[0]
        for f in files[base]:
            parts = self.get_parts(f)
            self.create_parts(parent, parts, base)

        results = self.count.values()
        results.append(self.utils.obj_to_path(parent))
        return results

    def prep_files(self, files, ignore, base):
        results = {base: []}
        files = self.ignore_parts(files, ignore)
        for f in files:
            results[base].append(self.utils.join_input(f, '/'))
        return results

    def set_image(self, image, obj, prefix_path, base):
        f = open('/'.join([base, self.utils.join_input(prefix_path, '/'),
            obj]), 'rb')
        data = f.read()
        f.close()
        image.setImage(data)
        commit()

    def set_page(self, page, obj, prefix_path, base):
        results = ''
        f = open('/'.join([base, self.utils.join_input(prefix_path, '/'),
            obj]), 'rb')
        data = f.read()
        f.close()
        root = fromstring(data)
        for element in root.iter():
            tag = element.tag
            text = element.text
            if tag in self.target_tags and text is not None:
                results += '<%s>%s</%s>' % (tag, text, tag)
        page.setText(results)
        commit()

    def set_title(self, obj, title):
        obj.setTitle(title.title())
        obj.reindexObject()
        commit()

    def setup_app(self, app):
        app = makerequest(app)
        newSecurityManager(None, system)
        return app


class Recipe(object):
    """zc.buildout recipe"""

    def __init__(self, buildout, name, options):
        self.buildout, self.name, self.options = buildout, name, options

    def install(self):
        """Installer"""

        utils = Utils()
        bindir = self.buildout['buildout']['bin-directory']
        [force, html_extensions, target_tags, path, illegal_chars,
            image_extensions] = utils.convert_recipe_options(self.options)

        arguments = "app, path='%s', illegal_chars='%s', html_extensions='%s',"
        arguments += " image_extensions='%s', target_tags='%s', force='%s'"

        # http://pypi.python.org/pypi/zc.buildout#the-scripts-function
        create_scripts([('import', 'parse2plone', 'main')],
            working_set, executable, bindir, arguments=arguments % (
            path, illegal_chars, html_extensions, image_extensions,
            target_tags, force))
        return tuple()

    def update(self):
        """Updater"""
        pass


def main(app, path=None, illegal_chars=None, html_extensions=None,
    image_extensions=None, target_tags=None, force=None):
    """parse2plone"""

    utils = Utils()
    logger = setup_logger()
    count = {'folders': 0, 'images': 0, 'pages': 0}

    # Clean recipe input
    [illegal_chars, html_extensions, image_extensions, target_tags,
        path, force] = utils.clean_recipe_input(illegal_chars,
        html_extensions, image_extensions, target_tags, path, force)

    # Process command line args
    option_parser = utils.create_option_parser()
    options, args = option_parser.parse_args()
    import_dir = args[0]
    [illegal_chars, html_extensions, image_extensions, target_tags,
        path, force] = utils.process_command_line_args(options,
        illegal_chars, html_extensions, image_extensions, target_tags,
        path, force)

    # Run parse2plone
    parse2plone = Parse2Plone()
    parse2plone = utils.setup_attrs(parse2plone, utils, count,
        illegal_chars, html_extensions, image_extensions, target_tags,
        logger)
    files = parse2plone.get_files(import_dir)
    ignore = len(utils.split_input(import_dir, '/'))
    app = parse2plone.setup_app(app)
    base = parse2plone.get_base(files, ignore)
    if utils.check_exists_path(app, path):
        parent = parse2plone.get_parent(app, path)
    else:
        if force:
            parse2plone.create_parts(app, parse2plone.get_parts(path), base)
            parent = parse2plone.get_parent(app, path)
        else:
            msg = "object in path '%s' does not exist, use --force to create"
            logger.info(msg % path)
            exit(1)
    files = parse2plone.prep_files(files, ignore, base)
    results = parse2plone.import_files(parent, files, base)

    # Print results
    msg = "Imported %s folders, %s images, and %s pages into: '%s'."
    logger.info(msg % tuple(results))
    exit(0)
