###############################################################################
#                                                                             #
# Parse2Plone - Easily import static website content into Plone               #
# Copyright (C) 2010 Alex Clark                                               #
#                                                                             #
# This program is free software; you can redistribute it and/or               #
# modify it under the terms of the GNU General Public License                 #
# as published by the Free Software Foundation; either version 2              #
# of the License, or (at your option) any later version.                      #
#                                                                             #
# This program is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with this program; if not, write to the Free Software                 #
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301,  #
# USA.                                                                        #
#                                                                             #
# Usage:                                                                      #
#                                                                             #
#     $ bin/plone run bin/import /path/to/files                               #
#                                                                             #
# See README.txt for more information                                         #
#                                                                             #
###############################################################################

import fnmatch
import logging
import lxml
import optparse
import re

from os import path as os_path
from os import walk
from pkg_resources import working_set
from sys import executable
from zc.buildout.easy_install import scripts as create_scripts

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
    'typeswap': None,
    'match': None,
}

_CONTENT = {
    'Document': 'Document',
    'Folder': 'Folder',
}

paths = re.compile('\n(\S+)\s+(\S+)')
slug = re.compile('(\d\d\d\d)/(\d\d)/(\d\d)/(.+)/index.html')


# BBB Because the ast module is not included with Python 2.4, we include this
# function to produce similar results (with our limited input set).
def fake_literal_eval(input):
    """
    Returns False when 'False' is passed in, and so on.
    """
    if input == 'False':
        return False
    elif input == 'True':
        return True
    elif input == 'None':
        return None
    else:
        return ValueError, 'malformed string'


def match_files(files, base, match):
    """
    Adds match feature to ``parse2plone``.

    The user may specify a string to match file names against; only content
    from files that match the string will be imported. E.g.

        $ bin/plone run bin/import /var/www/html --match=2000

    Will import:

        /var/www/html/2000/01/01/foo/index.html

    But not:

        /var/www/html/2001/01/01/foo/index.html
    """
    results = {base: []}
    for f in files[base]:
        for m in match:
            if f.find(m) >= 0:
                results[base].append(f)
    return results


# These next two functions add rename support to ``parse2plone``.
#
# This feature allows the user to specify two paths: old and new (e.g.
# --rename=old:new ).
#
# Then if a path like this is found:
#    /old/2000/01/01/foo/index.html
#
# Instead of creating /old/2000/01/01/foo/index.html (in Plone),
# ``parse2plone`` will create:
#
#    /new/2000/01/01/foo/index.html

def get_paths_to_rename(value):
    results = None
    if paths.findall(value):
        results = []
        for group in paths.findall(value):
            results.append('%s:%s' % (clean_path(group[0]),
                clean_path(group[1])))
        results = ','.join(results)
    return results


def rename_old_to_new(files, rename_map, base, rename):
    """
    Returns a rename_map which is forward/reverse mapping of old paths to
    new paths and vice versa. E.g.:

        rename_map{'forward': {'/var/www/html/old/2000/01/01/foo/index.html':
            '/var/www/html/new/2000/01/01/foo/index.html'}}

        rename_map{'reverse': {'/var/www/html/new/2000/01/01/foo/index.html':
            '/var/www/html/old/2000/01/01/foo/index.html'}}
    """
    for f in files[base]:
        for path in rename:
            parts = path.split(':')
            old = parts[0]
            new = parts[1]
            if f.find(old) >= 0:
                rename_map['forward'][f] = f.replace(old, new)
            rename_map['reverse'][f.replace(old, new)] = f
    return rename_map


# This next function adds
# "slugify" support to parse2plone, which means that if a path like this
# is discovered:
#
#     /2000/01/01/foo/index.html
#
# And --slugify is called, then instead of creating /2000/01/01/foo/index.html
# (in Plone), parse2plone will create:
#
#     /foo-20000101.html
#
# thereby "slugifying" the content, if you will.

def convert_path_to_slug(files, slug_map, base):

    """
    Returns a slug_map which is forward/reverse mapping of paths to slugified
    paths and vice versa. E.g.:

        slug_map{'forward': {'/var/www/html/2000/01/01/foo/index.html':
            '/var/www/html/foo-20000101.html'}}

        slug_map{'reverse': {'/var/www/html/foo-20000101.html':
            '/var/www/html/2000/01/01/foo/index.html'}}
    """

    for f in files[base]:
        result = slug.search(f)
        if result:
            groups = result.groups()
            slugfile = '%s-%s%s%s.html' % (groups[3], groups[0], groups[1],
                groups[2])
            slug_map['forward'][f] = slugfile
            slug_map['reverse'][slugfile] = f

    return slug_map


# These next two functions adds "typeswap" feature to ``parse2plone``.
#
# This feature allows the user to specify customize content types for use
# when importing content by specifying a "default" content type followed by
# its replacement "custom" content type (e.g.
# --typeswap=Document:MyCustomPageType).
#
# That means that instead of calling:
#   parent.invokeFactory('Document','foo')
#
# ``parse2plone`` will call:
#   parent.invokeFactory('MyCustomPageType','foo')

def get_types_to_swap(value):
    results = None
    if paths.findall(value):
        results = []
        for group in paths.findall(value):
            results.append('%s:%s' % (clean_path(group[0]),
                clean_path(group[1])))
        results = ','.join(results)
    return results


def swap_types(typeswap, _CONTENT, logger):
    """
    Update _CONTENT
    """
    for swap in typeswap:
        types = swap.split(':')
        old = types[0]
        new = types[1]
        if old in _CONTENT:
            _CONTENT[old] = new
        else:
            logger.error("Can't swap '%s' with unknown type: '%s'" % (new,
                old))
            exit(1)

    return _CONTENT


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


def clean_path(path):
    if path.startswith('/'):
        path = path[1:]
    if path.endswith('/'):
        path = path[0:-1]
    return path


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

    def convert_arg_values(self, illegal_chars, html_extensions,
        image_extensions, file_extensions, target_tags, path, force,
        publish, slugify, rename, typeswap, match):
        """
        Convert most recipe parameter values from csv; save results
        in _SETTINGS dict
        """
        _SETTINGS['illegal_chars'] = illegal_chars.split(',')
        _SETTINGS['html_extensions'] = html_extensions.split(',')
        _SETTINGS['image_extensions'] = image_extensions.split(',')
        _SETTINGS['file_extensions'] = file_extensions.split(',')
        _SETTINGS['target_tags'] = target_tags.split(',')
        _SETTINGS['path'] = clean_path(path)
        _SETTINGS['force'] = force
        _SETTINGS['publish'] = publish
        _SETTINGS['slugify'] = slugify
        if rename is not None:
            _SETTINGS['rename'] = rename.split(',')
        else:
            _SETTINGS['rename'] = rename
        if typeswap is not None:
            _SETTINGS['typeswap'] = typeswap.split(',')
        else:
            _SETTINGS['typeswap'] = typeswap
        if match is not None:
            _SETTINGS['match'] = match.split(',')
        else:
            _SETTINGS['match'] = match

    def create_option_parser(self):
        option_parser = optparse.OptionParser()
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
        option_parser.add_option("--typeswap", dest="typeswap",
            help="Optionally swap content types (see typeswap.py)")
        option_parser.add_option("--match", dest="match",
            help="Only import content that matches pattern (see match.py)")
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
        results = True
        if obj[:1] in illegal_chars:
            results = False
        return results

    def obj_to_path(self, obj):
        return '/'.join(obj.getPhysicalPath())

    def process_recipe_parameter_values(self, options):
        """
        Convert most recipe parameter values to csv; save in _SETTINGS dict
        """
        for option, existing_value in _SETTINGS.items():
            if option in options:
                if option in ('force', 'publish', 'slugify'):
                    value = fake_literal_eval(options[option].capitalize())
                elif option in ('rename'):
                    value = get_paths_to_rename((options[option]))
                elif option in ('typeswap'):
                    value = get_types_to_swap((options[option]))
                elif option not in ('path'):
                    value = ','.join(re.split('\s+', options[option]))
            else:
                if option in ('force', 'publish', 'slugify', 'rename',
                    'typeswap', 'path'):
                    value = existing_value
                else:
                    value = ','.join(existing_value)

            _SETTINGS[option] = value

    def process_command_line_args(self, options):
        """
        Process command line args; save results in _SETTINGS dict
        """
        if options.path is not None:
            _SETTINGS['path'] = clean_path(options.path)
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
        if options.typeswap is not None:
            _SETTINGS['typeswap'] = (options.typeswap).split(',')
        if options.match is not None:
            _SETTINGS['match'] = (options.match).split(',')

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

    def setup_locals(self, *kwargs):
        results = []
        for arg in kwargs:
            results.append(_SETTINGS[arg])
        return results


class Parse2Plone(object):
    """
    Parse2Plone
    """
    def create_content(self, parent, obj, prefix_path, base, slug_map,
        rename_map):
        # BBB Move imports here to avoid calling them on script installation,
        # makes parse2plone work with Plone 2.5 (non-egg release).
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
        folder_type = _CONTENT['Folder']
        parent.invokeFactory(folder_type, obj)
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
        page_type = _CONTENT['Document']
        parent.invokeFactory(page_type, obj)
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

    def get_base(self, import_dir, num_parts):
        import_dir = clean_path(import_dir)
        return '/'.join(import_dir.split('/')[:num_parts])

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

    def ignore_parts(self, files, num_parts):
        results = []
        for f in files:
            parts = self.get_parts(f)
            parts = parts[num_parts:]
            results.append(parts)
        return results

    def import_files(self, parent, files, base, slug_map, rename_map):
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

    def prep_files(self, files, num_parts, base):
        results = {base: []}
        files = self.ignore_parts(files, num_parts)
        for f in files:
            results[base].append('/'.join(f))
        return results

    def process_root(self, results, root):
        # separate out the XPath selectors and ordinary tags
        selectors = [x for x in self.target_tags if '/' in x]
        tags = [x for x in self.target_tags if '/' not in x]
        # if we have selectors, replace the "root" document with a tree
        # containing only the matched elements
        if selectors:
            elements = root.xpath('|'.join(selectors))
            root = lxml.etree.Element('fragment')
            for x in elements:
                root.append(x)
        else:
            elements = []
        # if there are non-XPath tags, we will select just the Text
        # nodes from within them
        if tags:
            for element in root.iter():
                tag = element.tag
                text = element.text
                if tag in self.target_tags and text is not None:
                    results += '<%s>%s</%s>' % (tag, text, tag)
        else:
            # if we have XPath selectors, but no other tags, return the
            # entire contents of the selected elements
            for element in elements:
                results += lxml.etree.tostring(element)
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
            root = lxml.html.fromstring(data)
        except lxml.etree.XMLSyntaxError:
            msg = "unable to import data from '%s', "
            msg = "make sure file contains HTML"
            self.logger.error(msg % filename)
            exit(1)
        results = self.process_root(results, root)
        page.setText(results)

    def set_state(self, obj):
        obj.portal_workflow.doActionFor(obj, 'publish')

    def set_title(self, obj, title):
        obj.setTitle(title.title())
        obj.reindexObject()

    def setup_app(self, app):
        # BBB Move imports here to avoid calling them on script installation,
        # makes parse2plone work with Plone 2.5 (non-egg release).
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
        utils.process_recipe_parameter_values(self.options)
        arguments = "app, path='%s', illegal_chars='%s', html_extensions='%s',"
        arguments += " image_extensions='%s', file_extensions='%s',"
        arguments += " target_tags='%s', force=%s, publish=%s,"
        arguments += " slugify=%s,"
        if _SETTINGS['rename']:
            arguments += " rename='%s',"
        else:
            arguments += " rename=%s,"
        if _SETTINGS['typeswap']:
            arguments += " typeswap='%s',"
        else:
            arguments += " typeswap=%s,"
        if _SETTINGS['match']:
            arguments += " match='%s'"
        else:
            arguments += " match=%s"

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
            _SETTINGS['typeswap'],
            _SETTINGS['match'],
            ))
        return tuple((bindir + '/' + 'import',))

    def update(self):
        """Updater"""
        pass


def main(app, path=None, illegal_chars=None, html_extensions=None,
    image_extensions=None, file_extensions=None, target_tags=None,
    force=False, publish=False, slugify=False, rename=None, typeswap=None,
    match=None):

    count = {'folders': 0, 'images': 0, 'pages': 0, 'files': 0}
    logger = setup_logger()
    rename_map = {'forward': {}, 'reverse': {}}
    slug_map = {'forward': {}, 'reverse': {}}
    utils = Utils()

    # Convert arg values from csv to list; save results in _SETTINGS
    utils.convert_arg_values(illegal_chars, html_extensions, image_extensions,
        file_extensions, target_tags, path, force, publish, slugify, rename,
        typeswap, match)

    # Process command line args; save results in _SETTINGS
    option_parser = utils.create_option_parser()
    options, args = option_parser.parse_args()
    import_dir = clean_path(args[0])
    utils.process_command_line_args(options)

    # Run parse2plone
    parse2plone = Parse2Plone()
    parse2plone = utils.setup_attrs(parse2plone, count, logger, utils)
    files = parse2plone.get_files(import_dir)
    num_parts = len(import_dir.split('/'))
    app = parse2plone.setup_app(app)
    base = parse2plone.get_base(import_dir, num_parts)
    path, force, slugify, rename, typeswap, match = utils.setup_locals('path',
        'force', 'slugify', 'rename', 'typeswap', 'match')
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
    files = parse2plone.prep_files(files, num_parts, base)
    if match:
        files = match_files(files, base, match)
    if slugify:
        slug_map = convert_path_to_slug(files, slug_map, base)
    if rename:
        rename_map = rename_old_to_new(files, rename_map, base, rename)
    if typeswap:
        swap_types(typeswap, _CONTENT, logger)
    results = parse2plone.import_files(parent, files, base, slug_map,
        rename_map)

    # Print results
    msg = "Imported %s folders, %s images, %s pages, and %s files into: '%s'."
    logger.info(msg % tuple(results))
    exit(0)
