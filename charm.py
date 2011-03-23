###############################################################################
#                                                                             #
# charm - Import static website content from the file system into Plone.      #
#                                                                             #
# Copyright (C) 2011 Alex Clark                                               #
#                                                                             #
# This program is free software; you can redistribute it and/or               #
# modify it under the terms of the GNU General Public License                 #
# as published by the Free Software Foundation; either version 2              #
# of the License, or (at your option) any later version.                      #
#                                                                             #
# This program is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the                #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with this program; if not, write to the Free Software                 #
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301,   #
# USA.                                                                        #
#                                                                             #
# Usage:                                                                      #
#                                                                             #
# $ bin/plone run bin/charm /path/to/files                                    #
#                                                                             #
# Where:                                                                      #
#                                                                             #
# * `bin/plone` is an instance script created by                              #
# http://pypi.python.org/pypi/plone.recipe.zope2instance                      #
# (after you run Buildout)                                                    #
#                                                                             #
# * `run` is a command line option of `bin/plone` to execute a script         #
#                                                                             #
# * `bin/charm` is a script created by parse2plone (after you run             #
# Buildout)                                                                   #
#                                                                             #
# * `/path/to/files` is the file system path to your website files e.g.       #
# /var/www/html                                                               #
#                                                                             #
# See README.txt for more information                                         #
#                                                                             #
###############################################################################

import logging
import lxml
import lxml.html
import optparse
import os
import pkg_resources
import re
import sys

from os import path as os_path
from sys import executable
from zc.buildout.easy_install import scripts as create_scripts

_SETTINGS = {
    'collapse': False,
    'create_spreadsheet': False,
    'encoding': 'utf8',
    'file_extensions': ['doc', 'mp3', 'xls'],
    'force': False,
    'html_extensions': ['html'],
    'ignore_errors': False,
    'illegal_chars': ['_', '.', '+'],
    'image_extensions': ['gif', 'jpg', 'jpeg', 'png'],
    'match': None,
    'path': '/Plone',
    'publish': False,
    'rename': None,
    'replacetypes': None,
    'target_tags': ['a', 'abbr', 'acronym', 'address',
        'applet', 'area', 'b', 'base', 'basefont', 'bdo',
        'big', 'blockquote', 'body', 'br', 'button', 'caption',
        'center', 'cite', 'code', 'col', 'colgroup', 'dd', 'del',
        'dfn', 'dir', 'div', 'dl', 'dt', 'em', 'fieldset', 'font',
        'form', 'frame', 'frameset', 'h1', 'h2', 'h3', 'h4', 'h5',
        'h6', 'head', 'hr', 'html', 'i', 'iframe', 'img', 'input',
        'ins', 'isindex', 'kbd', 'label', 'legend', 'li', 'link',
        'map', 'menu', 'meta', 'noframes', 'noscript', 'object',
        'ol', 'optgroup', 'option', 'p', 'param', 'pre', 'q', 's',
        'samp', 'script', 'select', 'small', 'span', 'strike',
        'strong', 'style', 'sub', 'sup', 'table', 'tbody', 'td',
        'textarea', 'tfoot', 'th', 'thead', 'title', 'tr', 'tt',
        'u', 'ul', 'var'],
    'user': 'admin',
}


def _setup_logger():
    # log levels: debug, info, warn, error, critical
    logger = logging.getLogger("charm")
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    outfile = logging.FileHandler(filename='charm.log')
    handler.setLevel(logging.INFO)
    outfile.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.addHandler(outfile)
    return logger

_COUNT = {'folders': 0, 'images': 0, 'pages': 0, 'files': 0}
_LOG = _setup_logger()
_UNSET_OPTION = ''


# Adds "create spreadsheet" feature to ``parse2plone``.
def create_spreadsheet(page, obj, parent_path, import_dir):
    """
    You can optionally tell ``parse2plone`` to try and import the contents of
    any spreadsheets it finds, by doing this::

    $ bin/plone run bin/import --create-spreadsheet /var/www/html

    If /var/www/html/foo.xls exists and has content, then a
    http://localhost:8080/Plone/foo will be created as a page, with the
    contents of the spreadsheet in an HTML table.

    This option will import all content to a single page.
    """
    import xlrd
    filename = '/'.join([import_dir, '/'.join(parent_path), obj])
    results = '<table>'
    wb = xlrd.open_workbook(filename)
    for sheet in wb.sheets():
        for row in range(sheet.nrows):
            results += '<tr>'
            for col in sheet.row(row):
                results += '<td>%s</td>' % col.value
            results += '</tr>'
    results += '</table>'
    page.setText(results)


# Adds "match" feature to ``parse2plone``.
def match_files(files, import_dir, match):
    """
    The user may specify a string to match file names against; only content
    from files that match the string will be imported. E.g.

    $ bin/plone run bin/import /var/www/html --match=2000

    Will import:

    /var/www/html/2000/01/01/foo/index.html

    But not:

    /var/www/html/2001/01/01/foo/index.html
    """
    results = {import_dir: []}
    for f in files[import_dir]:
        for m in match:
            if f.find(m) >= 0:
                results[import_dir].append(f)

    return results


# Adds "rename" feature to ``parse2plone``.
def rename_parts(files, _rename_map, import_dir, rename):
    """
    This allows the user to specify two paths: old and new (e.g.
    --rename=old:new ).

    Then if a path like this is found:
    /old/2000/01/01/foo/index.html

    Instead of creating /old/2000/01/01/foo/index.html (in Plone),
    ``parse2plone`` will create:

    /new/2000/01/01/foo/index.html

    This function returns a _rename_map which is forward/reverse mapping of
    old paths to new paths and vice versa. E.g.:

    _rename_map{'forward': {'/var/www/html/old/2000/01/01/foo/index.html':
    '/var/www/html/new/2000/01/01/foo/index.html'}}

    _rename_map{'reverse': {'/var/www/html/new/2000/01/01/foo/index.html':
    '/var/www/html/old/2000/01/01/foo/index.html'}}
    """
    for f in files[import_dir]:
        for path in rename:
            parts = path.split(':')
            old = parts[0]
            new = parts[1]
            if f.find(old) >= 0:
                _rename_map['forward'][f] = f.replace(old, new)
                _rename_map['reverse'][f.replace(old, new)] = f
    return _rename_map


# Adds "collapse" feature to ``parse2plone``.
def collapse_parts(object_paths, _collapse_map, import_dir):
    """
    If a path like this is discovered:

    /2000/01/01/foo/index.html

    And --collapse is called, then instead of creating
    /2000/01/01/foo/index.html (in Plone), parse2plone will create:

    /foo-20000101.html

    thereby "collapsing" the content, if you will.

    This function returns a _collapse_map which is forward/reverse mapping of
    paths to collapsed paths and vice versa. E.g.:

    _collapse_map{'forward': {'/var/www/html/2000/01/01/foo/index.html':
    '/var/www/html/foo-20000101.html'}}

    _collapse_map{'reverse': {'/var/www/html/foo-20000101.html':
    '/var/www/html/2000/01/01/foo/index.html'}}
    """
    expr = re.compile('(\d\d\d\d)/(\d\d)/(\d\d)/(.+)/index.html')
    for f in object_paths[import_dir]:
        result = expr.search(f)
        if result:
            groups = result.groups()
            collapse_id = '%s-%s%s%s.html' % (groups[3], groups[0], groups[1],
                groups[2])
            _collapse_map['forward'][f] = collapse_id
            _collapse_map['reverse'][collapse_id] = f
    return _collapse_map


# Adds "replacetypes" feature to ``parse2plone``.
def replace_types(replacetypes, _replace_types_map):
    """
    This allows the user to specify customize content types for use
    when importing content, by specifying a "default" content type followed by
    its replacement "custom" content type (e.g.
    --replacetypes=Document:MyCustomPageType).

    That means that instead of calling:
    parent.invokeFactory('Document','foo')

    ``parse2plone`` will call:
    parent.invokeFactory('MyCustomPageType','foo')

    Update _replace_types_map with new types.
    """
    for replace in replacetypes:
        types = replace.split(':')
        old = types[0]
        new = types[1]
        if old in _replace_types_map:
            _replace_types_map[old] = new
        else:
            raise ValueError
    return _replace_types_map


class Utils(object):
    def _clean_path(self, path):
        """
        Turns '/foo/bar/baz/' into 'foo/bar/baz'
        """
        if path.startswith('/'):
            path = path[1:]
        if path.endswith('/'):
            path = path[0:-1]
        return path

    def _check_exists_obj(self, parent, obj):
        if obj in parent.objectIds():
            return True
        else:
            return False

    def _check_exists_path(self, parent, path):
        try:
            parent.restrictedTraverse(path)
            return True
        except:
            return False

    def _convert_obj_to_path(self, obj):
        return '/'.join(obj.getPhysicalPath())

    def _convert_lines_to_csv(self, value):
        """
        Converts '\nfoo bar\nbaz qux' to 'foo:bar,baz:qux'
        """
        expr = re.compile('\n(\S+)\s+(\S+)')
        results = ""
        c = 0
        groups = expr.findall(value)
        for group in groups:
            results += '%s:%s' % (group[0], group[1])
            if c < len(groups) - 1:
                results += ','
            c += 1
        return results

    def _convert_str_to_csv(self, value):
        """
        Converts "foo bar baz" to "foo,bar,baz"
        """
        values = value.split(' ')
        results = ','.join(values)
        return results

    def _convert_tuple_to_params(self, params):
        """
        Converts [('foo','bar')] to foo="bar"
        """
        results = ""
        for param in params:
            results += (' %s="%s"' % (param[0], param[1]))
        return results

    def _create_option_parser(self):
        option_parser = optparse.OptionParser()
        option_parser.add_option('-u', '--user',
            default=_UNSET_OPTION,
            dest='user',
            help='Zope2 instance or Plone site user.')
        option_parser.add_option('-p', '--path',
            default=_UNSET_OPTION,
            dest='path',
            help='Path to Plone site object or sub-folder')
        option_parser.add_option('--html-extensions',
            default=_UNSET_OPTION,
            dest='html_extensions',
            help='Specify HTML file extensions')
        option_parser.add_option('--illegal-chars',
            default=_UNSET_OPTION,
            dest='illegal_chars',
            help='Specify characters to ignore')
        option_parser.add_option('--image-extensions',
            default=_UNSET_OPTION,
            dest='image_extensions',
            help='Specify image file extensions')
        option_parser.add_option('--file-extensions',
            default=_UNSET_OPTION,
            dest='file_extensions',
            help='Specify generic file extensions')
        option_parser.add_option('--target-tags',
            default=_UNSET_OPTION,
            dest='target_tags',
            help='Specify HTML tags to parse')
        option_parser.add_option('--force',
            action='store_true',
            default=_UNSET_OPTION,
            dest='force',
            help='Force creation of folders')
        option_parser.add_option('--publish',
            action='store_true',
            default=_UNSET_OPTION,
            dest='publish',
            help='Optionally publish newly created content')
        option_parser.add_option('--collapse',
            action='store_true',
            default=_UNSET_OPTION,
            dest='collapse',
            help="""Optionally "collapse" content (see collapse_parts())""")
        option_parser.add_option('--rename',
            default=_UNSET_OPTION,
            dest='rename',
            help='Optionally rename content (see rename_parts())')
        option_parser.add_option('--replace-types',
            default=_UNSET_OPTION,
            dest='replacetypes',
            help='Optionally use custom content types (see replace types())')
        option_parser.add_option('--match',
            default=_UNSET_OPTION,
            dest='match',
            help='Only import content that matches PATTERN (see match_files())'
            )
        option_parser.add_option('--create-spreadsheet',
            action='store_true',
            default=_UNSET_OPTION,
            dest='create_spreadsheet',
            help='Import contents of spreadsheet (see create_spreadsheet())')
        option_parser.add_option('--ignore-errors',
            action='store_true',
            default=_UNSET_OPTION,
            dest='ignore_errors',
            help='Ignore errors and keep going!')
        option_parser.add_option('--encoding',
            default=_UNSET_OPTION,
            dest='encoding',
            help='The charset to decode')
        return option_parser

    # BBB Because the ast module is not included with Python 2.4, we
    # include this function to produce similar results (with our
    # limited input set).
    def _fake_literal_eval(self, input):
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

    def _get_results(self, paths_map, index):
        results = ""
        max = len(paths_map)
        c = 0
        for i in paths_map:
            results += i.split(':')[index]
            c += 1
            if c != max:
                results += ','
        return "'%s'" % results

    def _get_files(self, import_dir):
        results = []
        for path, subdirs, files in os.walk(import_dir):
            _LOG.info("path '%s', has subdirs '%s', and files '%s'" % (
                path, ' '.join(subdirs), ' '.join(files)))

            for f in files:
                for crit in _SETTINGS['match']:
                    if f.find(crit) >= 0:
                        if self._is_legal(f):
                            if self._is_legal(self._get_obj(path)):
                                results.append(os_path.join(path, f))
                            else:
                                _LOG.info("path '%s' has illegal chars, skipping"
                                    % path)
                        else:
                            _LOG.info("file '%s' has illegal chars, skipping" % f)
                    else:
                        _LOG.info("file '%s' does not match '%s', skipping" % (f,
                            crit))

        return results

    def _get_obj(self, path):
        return path.split('/')[-1:][0]

    def _get_parts(self, path):
        path = self._clean_path(path)
        return path.split('/')

    def _get_path(self, parts, i):
        return '/'.join(parts[:i + 1])

    def _get_parent_parts(self, path):
        return path.split('/')[:-1]

    def _is_file(self, obj, extensions):
        result = False
        for ext in extensions:
            if obj.endswith(ext):
                result = True
        return result

    def _is_folder(self, obj):
        if len(obj.split('.')) == 1:
            return True
        else:
            return False

    def _is_legal(self, obj):
        # XXX Only checking the first char
        if obj[:1] in _SETTINGS['illegal_chars']:
            return False
        else:
            return True

    def process_command_line_args(self, options):
        """
        Process command line args
        """
        if options.user is not _UNSET_OPTION:
            _SETTINGS['user'] = options.user
        if options.path is not _UNSET_OPTION:
            _SETTINGS['path'] = self._clean_path(options.path)
        if options.illegal_chars is not _UNSET_OPTION:
            _SETTINGS['illegal_chars'] = options.illegal_chars
        if options.html_extensions is not _UNSET_OPTION:
            _SETTINGS['html_extensions'] = options.html_extensions
        if options.image_extensions is not _UNSET_OPTION:
            _SETTINGS['image_extensions'] = options.image_extensions
        if options.file_extensions is not _UNSET_OPTION:
            _SETTINGS['file_extensions'] = options.file_extensions
        if options.target_tags is not _UNSET_OPTION:
            _SETTINGS['target_tags'] = options.target_tags
        if options.force is not _UNSET_OPTION:
            _SETTINGS['force'] = options.force
        if options.publish is not _UNSET_OPTION:
            _SETTINGS['publish'] = options.publish
        if options.ignore_errors is not _UNSET_OPTION:
            _SETTINGS['ignore_errors'] = options.ignore_errors
        if options.encoding is not _UNSET_OPTION:
            _SETTINGS['encoding'] = options.encoding
        if options.collapse is not _UNSET_OPTION:
            _SETTINGS['collapse'] = options.collapse
        if options.create_spreadsheet is not _UNSET_OPTION:
            _SETTINGS['create_spreadsheet'] = options.create_spreadsheet
        if options.rename is not _UNSET_OPTION:
            _SETTINGS['rename'] = (options.rename).split(',')
        else:
            _SETTINGS['rename'] = None
        if options.replacetypes is not _UNSET_OPTION:
            _SETTINGS['replacetypes'] = (options.replacetypes).split(',')
        else:
            _SETTINGS['replacetypes'] = None
        if options.match is not _UNSET_OPTION:
            _SETTINGS['match'] = (options.match).split(',')

    def process_config_params(self, options):
        return "app=app"

    def _remove_parts(self, files, num_parts):
        results = []
        for f in files:
            parts = self._get_parts(f)
            parts = parts[num_parts:]
            results.append(parts)
        return results

    def _remove_base(self, files, num_parts, import_dir):
        results = {import_dir: []}
        files = self._remove_parts(files, num_parts)
        for f in files:
            results[import_dir].append('/'.join(f))
        return results

    def _remove_ext(self, obj):
        return obj.split('.')[0]

    def _set_encoding(self, data):
        return data.decode(_SETTINGS['encoding'])

    def _setup_app(self, app, user=None):
        # BBB Move imports here to avoid calling them on script installation,
        # makes parse2plone work with Plone 2.5 (non-egg release).
        if user == None:
            from AccessControl.SecurityManagement import newSecurityManager
            from AccessControl.SpecialUsers import system
            from Testing.makerequest import makerequest
            newSecurityManager(None, system)
            app = makerequest(app)
            return app
        else:
            from AccessControl.SecurityManagement import newSecurityManager
            from Testing.makerequest import makerequest
            user = app.acl_users.getUser(user)
            user = user.__of__(app.acl_users)
            newSecurityManager(None, user)
            app = makerequest(app)
            return app

    def _update_parent(self, current_parent, parent_path):
        updated_parent = current_parent.restrictedTraverse(parent_path)
        _LOG.info("updating parent from '%s' to '%s'" % (
             self._convert_obj_to_path(current_parent),
             self._convert_obj_to_path(updated_parent)))
        return updated_parent

    def _validate_recipe_args(self, options):
        for option in options:
            if not (option != 'recipe' or option != 'location'):
                if option not in _SETTINGS.keys():
                    return False
        return True


class Parse2Plone(object):
    def create_content(self, parent, obj, parent_path, import_dir,
        _collapse_map, _rename_map, _replace_types_map):
        # BBB Move imports here to avoid calling them on script installation,
        # makes parse2plone work with Plone 2.5 (non-egg release).
        from transaction import commit
        utils = Utils()
        if utils._is_folder(obj):
            folder = self.create_folder(parent, obj, _replace_types_map)
            self.set_title(folder, obj)
            _COUNT['folders'] += 1
            commit()
        elif utils._is_file(obj, _SETTINGS['html_extensions']):
            page = self.create_page(parent, obj, _replace_types_map)
            self.set_title(page, obj)
            self.set_page(page, obj, parent_path, import_dir, _collapse_map,
                _rename_map)
            _COUNT['pages'] += 1
            commit()
        elif utils._is_file(obj, _SETTINGS['image_extensions']):
            image = self.create_image(parent, obj, _replace_types_map)
            self.set_title(image, obj)
            self.set_image(image, obj, parent_path, import_dir)
            _COUNT['images'] += 1
            commit()
        elif utils._is_file(obj, _SETTINGS['file_extensions']):
            if not _SETTINGS['create_spreadsheet']:
                at_file = self.create_file(parent, obj, _replace_types_map)
                self.set_title(at_file, obj)
                self.set_file(at_file, obj, parent_path, import_dir)
                _COUNT['files'] += 1
                commit()
            else:
                # Try to import the contents of the spreadsheet
                if obj.endswith('.xls'):
                    if not utils._check_exists_obj(parent,
                            utils._remove_ext(obj)):
                        page = self.create_page(parent,
                            utils._remove_ext(obj),
                            _replace_types_map)
                        self.set_title(page, utils._remove_ext(obj))
                        create_spreadsheet(page, obj, parent_path,
                            import_dir)
                        _COUNT['files'] += 1
                        commit()
                    else:
                        _LOG.info("object '%s' exists inside '%s'" % (
                            obj, utils._convert_obj_to_path(parent)))

    def create_folder(self, parent, obj, _replace_types_map):
        utils = Utils()
        _LOG.info("creating folder '%s' inside parent folder '%s'" % (
            obj, utils._convert_obj_to_path(parent)))
        folder_type = _replace_types_map['Folder']
        parent.invokeFactory(folder_type, obj)
        folder = parent[obj]
        if _SETTINGS['publish']:
            self.set_state(folder)
            _LOG.info("publishing folder '%s'" % obj)
        return folder

    def create_file(self, parent, obj, _replace_types_map):
        utils = Utils()
        _LOG.info("creating file '%s' inside parent folder '%s'" % (obj,
            utils._convert_obj_to_path(parent)))
        parent.invokeFactory('File', obj)
        file = parent[obj]
        return file

    def create_image(self, parent, obj, _replace_types_map):
        utils = Utils()
        _LOG.info("creating image '%s' inside parent folder '%s'" % (
            obj, utils._convert_obj_to_path(parent)))
        parent.invokeFactory('Image', obj)
        image = parent[obj]
        return image

    def create_page(self, parent, obj, _replace_types_map):
        utils = Utils()
        _LOG.info("creating page '%s' inside parent folder '%s'" % (obj,
            utils._convert_obj_to_path(parent)))
        page_type = _replace_types_map['Document']
        parent.invokeFactory(page_type, obj)
        page = parent[obj]
        if _SETTINGS['publish']:
            self.set_state(page)
            _LOG.info("publishing page '%s'" % obj)
        return page

    def create_parts(self, parent, parts, import_dir, _collapse_map,
        _rename_map, _replace_types_map):

        _LOG.info("creating parts for '%s'" % '/'.join(parts))
        utils = Utils()

        for i in range(len(parts)):
            path = utils._get_path(parts, i)
            parent_path = utils._get_parent_parts(path)
            obj = utils._get_obj(path)
            parent = utils._update_parent(parent, '/'.join(parent_path))
            if utils._is_legal(obj):
                if utils._check_exists_obj(parent, obj):
                    _LOG.info("object '%s' exists inside '%s'" % (
                        obj, utils._convert_obj_to_path(parent)))
                else:
                    _LOG.info(
                        "object '%s' does not exist inside '%s'"
                        % (obj, utils._convert_obj_to_path(parent)))
                    self.create_content(parent, obj, parent_path, import_dir,
                        _collapse_map, _rename_map, _replace_types_map)
            else:
                _LOG.info("object '%s' has illegal chars" % obj)
                break

    def import_files(self, parent, object_paths, import_dir, _collapse_map,
        _rename_map, _replace_types_map):
        utils = Utils()
        for f in object_paths[import_dir]:
            parts = utils._get_parts(f)
            if _SETTINGS['rename'] and f in _rename_map['forward']:
                parts = _rename_map['forward'][f].split('/')
            if _SETTINGS['collapse'] and f in _collapse_map['forward']:
                parts = _collapse_map['forward'][f].split('/')
            if _SETTINGS['ignore_errors']:
                try:
                    self.create_parts(parent, parts, import_dir, _collapse_map,
                        _rename_map, _replace_types_map)
                except:
                    # Keep going!
                    _LOG.info("Keep going! Ignoring error '%s'"
                        % sys.exc_info()[1])
                    pass
            else:
                self.create_parts(parent, parts, import_dir, _collapse_map,
                    _rename_map, _replace_types_map)

    def parse_root(self, results, root):
        utils = Utils()
        # separate out the XPath selectors and ordinary tags
        selectors = [x for x in _SETTINGS['target_tags'] if '/' in x]
        tags = [x for x in _SETTINGS['target_tags'] if '/' not in x]
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
                params = element.items()
                if tag in _SETTINGS['target_tags'] and text is not None:
                    if params is []:
                        results += '<%s>%s</%s>' % (tag, text, tag)
                    else:
                        params = utils._convert_tuple_to_params(params)
                        results += '<%s %s>%s</%s>' % (tag, params, text, tag)
        else:
            # if we have XPath selectors, but no other tags, return the
            # entire contents of the selected elements
            for element in elements:
                results += lxml.etree.tostring(element)
        return results

    def set_image(self, image, obj, parent_path, import_dir):
        f = open('/'.join([import_dir, '/'.join(parent_path), obj]), 'rb')
        data = f.read()
        f.close()
        image.setImage(data)

    def set_file(self, at_file, obj, parent_path, import_dir):
        f = open('/'.join([import_dir, '/'.join(parent_path), obj]), 'rb')
        data = f.read()
        f.close()
        at_file.setFile(data)

    def set_page(self, page, obj, parent_path, import_dir, _collapse_map,
        _rename_map):
        utils = Utils()
        filename = '/'.join([import_dir, '/'.join(parent_path), obj])
        key = '/'.join(parent_path) + '/' + obj
        if _SETTINGS['rename'] and key in _rename_map['reverse']:
            value = _rename_map['reverse'][key]
            filename = '/'.join([import_dir, value])
        if _SETTINGS['collapse'] and obj in _collapse_map['reverse']:
            value = _collapse_map['reverse'][obj]
            filename = '/'.join([import_dir, value])
        f = open(filename, 'rb')
        results = ''
        data = f.read()
        f.close()
        data = utils._set_encoding(data)
        try:
            root = lxml.html.fromstring(data)
        except lxml.etree.XMLSyntaxError:
            msg = "unable to import data from '%s', "
            msg += "make sure file contains HTML."
            _LOG.error(msg % filename)
            exit(1)
        results = self.parse_root(results, root)
        page.setText(results)

    def set_state(self, obj):
        obj.portal_workflow.doActionFor(obj, 'publish')

    def set_title(self, obj, title):
        obj.setTitle(title.title())
        obj.reindexObject()


class Recipe(object):
    """zc.buildout recipe"""
    def __init__(self, buildout, name, options):
        self.buildout, self.name, self.options = buildout, name, options
        self.options['location'] = pkg_resources.working_set.find(
            pkg_resources.Requirement.parse('charm')).location


    def install(self):
        """Installer"""
        bindir = self.buildout['buildout']['bin-directory']

        utils = Utils()

        if not utils._validate_recipe_args(self.options):
            raise ValueError("Unknown recipe parameter in '%s'." %
                self.options)

        arguments = utils.process_config_params(self.options)

        # http://pypi.python.org/pypi/zc.buildout#the-scripts-function
        create_scripts([(self.name, 'charm', 'main')],
            pkg_resources.working_set, executable, bindir,
            arguments=arguments)

        return tuple((bindir + '/' + self.name,))

    def update(self):
        """Updater"""
        pass


def main(**kwargs):
    _rename_map = {'forward': {}, 'reverse': {}}
    _collapse_map = {'forward': {}, 'reverse': {}}
    _replace_types_map = {'Document': 'Document', 'Folder': 'Folder'}

    parse2plone = Parse2Plone()
    utils = Utils()

    # Make sure we have import dir, at least
    msg = "You must specify an import directory that exists e.g. /path/to/files "
    msg = "as the first positional argument. "
    msg += "See -h for more."
    if len(sys.argv) >= 2:
        if sys.argv[1] == '-h' or sys.argv[1] == '--help':
            # let optparse do its thing
            pass
        else:
            _SETTINGS['import_dir'] = sys.argv[1]
            try:
                os.stat(_SETTINGS['import_dir'])
            except OSError:
                _LOG.error(msg)
                exit(1)
    else:
        _LOG.error(msg)
        exit(1)

    # Process command line args; save results in _SETTINGS
    option_parser = utils._create_option_parser()
    options, args = option_parser.parse_args()
    utils.process_command_line_args(options)

    # Run parse2plone
    files = utils._get_files(_SETTINGS['import_dir'])
    num_parts = len(_SETTINGS['import_dir'].split('/'))
    app = utils._setup_app(kwargs['app'], user=_SETTINGS['user'])
    if utils._check_exists_path(app, _SETTINGS['path']):
        parent = utils._update_parent(app, _SETTINGS['path'])
    else:
        if _SETTINGS['force']:
            parse2plone.create_parts(app, utils._get_parts(_SETTINGS['path']),
                _SETTINGS['import_dir'], _collapse_map, _rename_map, _replace_types_map)
            parent = utils._update_parent(app, _SETTINGS['path'])
        else:
            msg = "object in path '%s' does not exist."
            _LOG.error(msg % _SETTINGS['path'])
            exit(1)
    object_paths = utils._remove_base(files, num_parts, _SETTINGS['import_dir'])
    if _SETTINGS['match']:
        object_paths = match_files(object_paths, _SETTINGS['import_dir'],
            _SETTINGS['match'])
    if _SETTINGS['collapse']:
        _collapse_map = collapse_parts(object_paths, _collapse_map,
        _SETTINGS['import_dir'])
    if _SETTINGS['rename']:
        _rename_map = rename_parts(object_paths, _rename_map, _SETTINGS['import_dir'],
        _SETTINGS['rename'])
    if _SETTINGS['replacetypes']:
        try:
            replace_types(_SETTINGS['replacetypes'], _replace_types_map)
        except ValueError:
            _LOG.error("Can't replace unknown type")
            exit(1)
    parse2plone.import_files(parent, object_paths, _SETTINGS['import_dir'],
        _collapse_map, _rename_map, _replace_types_map)

    # Print results
    msg = "Imported %s folders, %s images, %s pages, and %s files."
    _LOG.info(msg % (_COUNT['folders'], _COUNT['images'], _COUNT['pages'],
        _COUNT['files']))
    exit(0)
