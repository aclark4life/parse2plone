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
import re

from lxml.html import fromstring
from lxml.etree import XMLSyntaxError
from optparse import OptionParser
from os import path as os_path
from os import walk
from pkg_resources import working_set
from sys import executable
from zc.buildout.easy_install import scripts as create_scripts

from slugify import convert_path_to_slug
from rename import get_paths_to_rename, rename_old_to_new

_SETTINGS = {
    'path': '/Plone',
    'illegal_chars': ['_', '.'],
    'html_extensions': ['html'],
    'image_extensions': ['gif', 'jpg', 'jpeg', 'png'],
    'file_extensions': ['mp3'],
    'target_tags': ['a', 'div', 'h1', 'h2', 'p'],
    'force': False,
    'publish': False,
    'slugify': False,
    'rename': None,
}


def fake_literal_eval(input):
    """
    Because the ast module is not included with Python 2.4, we include this
    function to produce similar results (with our limited input set).
    """
    if input == 'False':
        return False
    elif input == 'True':
        return True
    elif input == 'None':
        return None


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
        if obj in parent.objectIds():
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

    def convert_arg_values(self, illegal_chars, html_extensions,
        image_extensions, file_extensions, target_tags, path, force,
        publish, slugify, rename):
        """
        Convert most recipe parameter values from csv; save results
        in _SETTINGS dict
        """
        _SETTINGS['illegal_chars'] = illegal_chars.split(',')
        _SETTINGS['html_extensions'] = html_extensions.split(',')
        _SETTINGS['image_extensions'] = image_extensions.split(',')
        _SETTINGS['file_extensions'] = file_extensions.split(',')
        _SETTINGS['target_tags'] = target_tags.split(',')
        _SETTINGS['path'] = self.clean_path(path)
        _SETTINGS['force'] = force
        _SETTINGS['publish'] = publish
        _SETTINGS['slugify'] = slugify
        if rename is not None:
            _SETTINGS['rename'] = rename.split(',')
        else:
            _SETTINGS['rename'] = rename

    def create_option_parser(self):
        option_parser = OptionParser()
        option_parser.add_option("-p", "--path", dest="path",
            help="Path to Plone site object or sub-folder")
        option_parser.add_option("--html-extensions",
            dest="html_extensions", help="Specify HTML file extensions")
        option_parser.add_option("--illegal-chars", dest="illegal_chars",
            help="Specify characters to ignore")
        option_parser.add_option("--image-extensions",
            dest="image_extensions", help="Specify image file extensions")
        option_parser.add_option("--file-extensions",
            dest="file_extensions", help="Specify generic file extensions")
        option_parser.add_option("--target-tags", dest="target_tags",
            help="Specify HTML tags to parse")
        option_parser.add_option("--force",
            action="store_true", dest="force", default=False,
            help="Force creation of folders")
        option_parser.add_option("--publish",
            action="store_true", dest="publish", default=False,
            help="Optionally publish newly created content")
        option_parser.add_option("--slugify",
            action="store_true", dest="slugify", default=False,
            help="""Optionally "slugify" content (see slugify.py)""")
        option_parser.add_option("--rename",
            dest="rename", help="Optionally rename content (see rename.py)")
        return option_parser

    def is_file(self, obj, extensions):
        result = False
        for ext in extensions:
            if obj.endswith(ext):
                result = True
        return result

    def is_folder(self, obj):
        if len(obj.split('.')) == 1:
            return True
        else:
            return False

    def is_legal(self, obj, illegal_chars):
        if not obj[0] in illegal_chars:
            return True
        else:
            return False

    def obj_to_path(self, obj):
        return '/'.join(obj.getPhysicalPath())

    def convert_parameter_values(self, options):
        """
        Convert most recipe parameter values to csv; save in _SETTINGS dict
        """
        for option, existing_value in _SETTINGS.items():
            if option in options:
                if option in ('force', 'publish', 'slugify'):
                    value = fake_literal_eval(options[option].capitalize())
                elif option in ('rename'):
                    value = get_paths_to_rename((options[option]))
                elif option in ('path'):
                    value = options[option]
                elif option not in ('path'):
                    value = ','.join(re.split('\s+', options[option]))
            else:
                if option in ('force', 'publish', 'slugify', 'rename', 'path'):
                    value = existing_value
                else:
                    value = ','.join(existing_value)

            _SETTINGS[option] = value

    def process_command_line_args(self, options):
        """
        Process command line args; save results in _SETTINGS dict
        """
        if options.path is not None:
            _SETTINGS['path'] = self.clean_path(options.path)
        if options.illegal_chars is not None:
            _SETTINGS['illegal_chars'] = options.illegal_chars
        if options.html_extensions is not None:
            _SETTINGS['html_extensions'] = options.html_extensions
        if options.image_extensions is not None:
            _SETTINGS['image_extensions'] = options.image_extensions
        if options.file_extensions is not None:
            _SETTINGS['file_extensions'] = options.file_extensions
        if options.target_tags is not None:
            _SETTINGS['target_tags'] = options.target_tags
        if options.force is not None:
            _SETTINGS['force'] = options.force
        if options.publish is not None:
            _SETTINGS['publish'] = options.publish
        if options.slugify is not None:
            _SETTINGS['slugify'] = options.slugify
        if options.rename is not None:
            _SETTINGS['rename'] = (options.rename).split(',')

    def setup_attrs(self, parse2plone, count, logger, utils):
        """
        Make settings available as Parse2Plone class attributes
        for convenience.
        """
        for option, value in _SETTINGS.items():
            setattr(parse2plone, option, value)
        parse2plone.count = count
        parse2plone.logger = logger
        parse2plone.utils = utils
        return parse2plone


class Parse2Plone(object):
    """
    Parse2Plone
    """
    def create_content(self, parent, obj, prefix_path, base, slug_map,
        rename_map):
        from transaction import commit
        if self.utils.is_folder(obj):
            folder = self.create_folder(parent, obj)
            self.set_title(folder, obj)
            self.count['folders'] += 1
            commit()
        elif self.utils.is_file(obj, self.html_extensions):
            page = self.create_page(parent, obj)
            self.set_title(page, obj)
            self.set_page(page, obj, prefix_path, base, slug_map, rename_map)
            self.count['pages'] += 1
            commit()
        elif self.utils.is_file(obj, self.image_extensions):
            image = self.create_image(parent, obj)
            self.set_title(image, obj)
            self.set_image(image, obj, prefix_path, base)
            self.count['images'] += 1
            commit()
        elif self.utils.is_file(obj, self.file_extensions):
            at_file = self.create_file(parent, obj)
            self.set_title(at_file, obj)
            self.set_file(at_file, obj, prefix_path, base)
            self.count['files'] += 1
            commit()

    def create_folder(self, parent, obj):
        self.logger.info("creating folder '%s' inside parent folder '%s'" % (
            obj, self.utils.obj_to_path(parent)))
        parent.invokeFactory('Folder', obj)
        folder = parent[obj]
        if self.publish:
            self.set_state(folder)
            self.logger.info("publishing folder '%s'" % obj)
        return folder

    def create_file(self, parent, obj):
        self.logger.info("creating file '%s' inside parent folder '%s'" % (obj,
            self.utils.obj_to_path(parent)))
        parent.invokeFactory('File', obj)
        file = parent[obj]
        return file

    def create_image(self, parent, obj):
        self.logger.info("creating image '%s' inside parent folder '%s'" % (
            obj, self.utils.obj_to_path(parent)))
        parent.invokeFactory('Image', obj)
        image = parent[obj]
        return image

    def create_page(self, parent, obj):
        self.logger.info("creating page '%s' inside parent folder '%s'" % (obj,
            self.utils.obj_to_path(parent)))
        parent.invokeFactory('Document', obj)
        page = parent[obj]
        if self.publish:
            self.set_state(page)
            self.logger.info("publishing page '%s'" % obj)
        return page

    def create_parts(self, parent, parts, base, slug_map, rename_map):
        self.logger.info("creating parts for '%s'" % '/'.join(parts))
        for i in range(len(parts)):
            path = self.get_path(parts, i)
            prefix_path = self.get_prefix_path(path)
            obj = self.get_obj(path)
            parent = self.get_parent(parent, '/'.join(prefix_path))
            if self.utils.is_legal(obj, self.illegal_chars):
                if self.utils.check_exists_obj(parent, obj):
                    self.logger.info("object '%s' exists inside '%s'" % (
                        obj, self.utils.obj_to_path(parent)))
                else:
                    self.logger.info(
                        "object '%s' does not exist inside '%s'"
                        % (obj, self.utils.obj_to_path(parent)))
                    self.create_content(parent, obj, prefix_path, base,
                        slug_map, rename_map)
            else:
                self.logger.info("object '%s' has illegal chars" % obj)
                break

    def get_base(self, files, ignore):
        return '/'.join(files[0].split('/')[:ignore])

    def get_files(self, import_dir):
        results = []
        for path, subdirs, files in walk(import_dir):
            self.logger.info("path '%s', has subdirs '%s', and files '%s'" % (
                path, ' '.join(subdirs), ' '.join(files)))
            for f in fnmatch.filter(files, '*'):
                if self.utils.is_legal(f, self.illegal_chars):
                    results.append(os_path.join(path, f))
                else:
                    self.logger.info("object '%s' has illegal chars" % f)
        return results

    def get_obj(self, path):
        return path.split('/')[-1:][0]

    def get_parent(self, current_parent, prefix_path):
        updated_parent = current_parent.restrictedTraverse(prefix_path)
        self.logger.info("updating parent from '%s' to '%s'" % (
             self.utils.obj_to_path(current_parent),
             self.utils.obj_to_path(updated_parent)))
        return updated_parent

    def get_parts(self, path):
        return path.split('/')

    def get_path(self, parts, i):
        return '/'.join(parts[:i + 1])

    def get_prefix_path(self, path):
        return path.split('/')[:-1]

    def ignore_parts(self, files, ignore):
        results = []
        for f in files:
            parts = self.get_parts(f)
            if ignore is not '':
                parts = parts[ignore:]
            results.append(parts)
        return results

    def import_files(self, parent, files, base, slug_map, rename_map):
        base = files.keys()[0]
        for f in files[base]:
            parts = self.get_parts(f)
            if self.rename and f in rename_map['forward']:
                parts = rename_map['forward'][f].split('/')
            if self.slugify and f in slug_map['forward']:
                parts = slug_map['forward'][f].split('/')
            self.create_parts(parent, parts, base, slug_map, rename_map)
        results = self.count.values()
        results.append(self.utils.obj_to_path(parent))
        return results

    def prep_files(self, files, ignore, base):
        results = {base: []}
        files = self.ignore_parts(files, ignore)
        for f in files:
            results[base].append('/'.join(f))
        return results

    def set_image(self, image, obj, prefix_path, base):
        f = open('/'.join([base, '/'.join(prefix_path), obj]), 'rb')
        data = f.read()
        f.close()
        image.setImage(data)

    def set_file(self, at_file, obj, prefix_path, base):
        f = open('/'.join([base, '/'.join(prefix_path), obj]), 'rb')
        data = f.read()
        f.close()
        at_file.setFile(data)

    def set_page(self, page, obj, prefix_path, base, slug_map, rename_map):
        filename = '/'.join([base, '/'.join(prefix_path), obj])
        key = '/'.join(prefix_path) + '/' + obj
        if self.rename and key in rename_map['reverse']:
            value = rename_map['reverse'][key]
            filename = '/'.join([base, value])
        if self.slugify and obj in slug_map['reverse']:
            value = slug_map['reverse'][obj]
            filename = '/'.join([base, value])
        f = open(filename, 'rb')
        results = ''
        data = f.read()
        f.close()
        try:
            root = fromstring(data)
        except XMLSyntaxError:
            msg = "unable to import data from '%s', "
            msg = "make sure file contains HTML"
            self.logger.error(msg % filename)
            exit(1)
        for element in root.iter():
            tag = element.tag
            text = element.text
            if tag in self.target_tags and text is not None:
                results += '<%s>%s</%s>' % (tag, text, tag)
        page.setText(results)

    def set_state(self, obj):
        obj.portal_workflow.doActionFor(obj, 'publish')

    def set_title(self, obj, title):
        obj.setTitle(title.title())
        obj.reindexObject()

    def setup_app(self, app):
        from AccessControl.SecurityManagement import newSecurityManager
        from AccessControl.SpecialUsers import system
        from Testing.makerequest import makerequest
        app = makerequest(app)
        newSecurityManager(None, system)
        return app


class Recipe(object):
    """zc.buildout recipe"""
    def __init__(self, buildout, name, options):
        self.buildout, self.name, self.options = buildout, name, options

    def install(self):
        """Installer"""
        bindir = self.buildout['buildout']['bin-directory']
        utils = Utils()
        utils.convert_parameter_values(self.options)

        arguments = "app, path='%s', illegal_chars='%s', html_extensions='%s',"
        arguments += " image_extensions='%s', file_extensions='%s',"
        arguments += " target_tags='%s', force=%s, publish=%s,"
        arguments += " slugify=%s, rename=%s"

        # http://pypi.python.org/pypi/zc.buildout#the-scripts-function
        create_scripts([('import', 'parse2plone', 'main')],
            working_set, executable, bindir, arguments=arguments % (
            _SETTINGS['path'],
            _SETTINGS['illegal_chars'],
            _SETTINGS['html_extensions'],
            _SETTINGS['image_extensions'],
            _SETTINGS['file_extensions'],
            _SETTINGS['target_tags'],
            _SETTINGS['force'],
            _SETTINGS['publish'],
            _SETTINGS['slugify'],
            _SETTINGS['rename'],
            ))
        return tuple()

    def update(self):
        """Updater"""
        pass


def main(app, path=None, illegal_chars=None, html_extensions=None,
    image_extensions=None, file_extensions=None, target_tags=None,
    force=None, publish=None, slugify=None, rename=None):
    """parse2plone"""
    count = {'folders': 0, 'images': 0, 'pages': 0, 'files': 0}
    logger = setup_logger()
    rename_map = {'forward': {}, 'reverse': {}}
    slug_map = {'forward': {}, 'reverse': {}}
    utils = Utils()

    # Convert arg values from csv to list; save results in _SETTINGS
    utils.convert_arg_values(illegal_chars, html_extensions, image_extensions,
        file_extensions, target_tags, path, force, publish, slugify, rename)

    # Process command line args; save results in _SETTINGS
    option_parser = utils.create_option_parser()
    options, args = option_parser.parse_args()
    import_dir = args[0]
    utils.process_command_line_args(options)

    # Run parse2plone
    parse2plone = Parse2Plone()
    parse2plone = utils.setup_attrs(parse2plone, count, logger, utils)
    files = parse2plone.get_files(import_dir)
    ignore = len(import_dir.split('/'))
    app = parse2plone.setup_app(app)
    base = parse2plone.get_base(files, ignore)
    path = _SETTINGS['path']
    force = _SETTINGS['force']
    slugify = _SETTINGS['slugify']
    rename = _SETTINGS['rename']
    if utils.check_exists_path(app, path):
        parent = parse2plone.get_parent(app, path)
    else:
        if force:
            parse2plone.create_parts(app, parse2plone.get_parts(path), base,
                slug_map, rename_map)
            parent = parse2plone.get_parent(app, path)
        else:
            msg = "object in path '%s' does not exist, use --force to create"
            logger.error(msg % path)
            exit(1)
    files = parse2plone.prep_files(files, ignore, base)
    if slugify:
        slug_map = convert_path_to_slug(files, slug_map, base)
    if rename:
        rename_map = rename_old_to_new(files, rename_map, base, rename)
    results = parse2plone.import_files(parent, files, base, slug_map,
        rename_map)

    # Print results
    msg = "Imported %s folders, %s images, %s pages, and %s files into: '%s'."
    logger.info(msg % tuple(results))
    exit(0)
