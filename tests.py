import unittest

from Products.CMFPlone.tests import PloneTestCase

PloneTestCase.setupPloneSite()


# Test "rename" feature
class RenameOldNewTestCase(unittest.TestCase):

    def setUp(self):
        self.rename_map_before = {'forward': {}, 'reverse': {}}
        self.rename_map_after = {
            'forward': {
                '/var/www/html/foo/index.html': '/var/www/html/bar/index.html',
                '/var/www/html/baz/index.html': '/var/www/html/qux/index.html'
            },
            'reverse': {
                '/var/www/html/bar/index.html': '/var/www/html/foo/index.html',
                '/var/www/html/qux/index.html': '/var/www/html/baz/index.html'}
            }
        self.base = '/var/www/html'
        self.files = {self.base: [
            '/var/www/html/foo/index.html',
            '/var/www/html/baz/index.html'
        ]}
        self.recipe_input_line_1 = "\n/foo /bar"
        self.recipe_input_line_2 = "\n/baz /qux"
        self.recipe_input_before = [self.recipe_input_line_1,
            self.recipe_input_line_2]
        self.recipe_input_after = ['/foo:/bar', '/baz:/qux']

    def testRenameOldNew(self):
        import parse2plone
        rename_map_before = self.rename_map_before
        rename_map_after = self.rename_map_after
        files = self.files
        base = self.base
        rename = ['foo:bar', 'baz:qux']
        self.assertEqual(rename_map_after,
            parse2plone.rename_parts(
            files, rename_map_before, base, rename))

    def testConvertRecipeInputToCSV(self):
        import parse2plone
        utils = parse2plone.Utils()
        results = []
        recipe_input_before = self.recipe_input_before
        recipe_input_after = self.recipe_input_after

        for recipe_input in recipe_input_before:
            results.append(utils._convert_str_to_csv(recipe_input))

        self.assertEqual(results, recipe_input_after)


# Test "match" feature
class MatchFilesTestCase(unittest.TestCase):

    def setUp(self):
        self.base = '/var/www/html'
        self.files_before = {self.base: [
            '/var/www/html/2000/index.html',
            '/var/www/html/2001/index.html'
        ]}
        self.files_after = {self.base: [
            '/var/www/html/2000/index.html',
        ]}

    def testMatchFiles(self):
        import parse2plone
        base = self.base
        files_before = self.files_before
        files_after = self.files_after
        self.assertEqual(files_after,
            parse2plone.match_files(files_before, base, ['2000']))


# Test "replacetypes" feature
class ReplaceTypesTestCase(unittest.TestCase):

    def setUp(self):
        self.replacetypes = ['Document:MyDocumentType', 'Folder:MyFolderType']
        self._replace_types_map_before = {
            'Document': 'Document',
            'Folder': 'Folder',
        }
        self._replace_types_map_after = {
            'Document': 'MyDocumentType',
            'Folder': 'MyFolderType',
        }

    def testReplaceTypes(self):
        import parse2plone
        map_before = self._replace_types_map_before
        map_after = self._replace_types_map_after
        types = self.replacetypes
        self.assertEqual(map_after,
            parse2plone.replace_types(types, map_before))


# Test "collapse" feature
class CollapseTestCase(unittest.TestCase):

    def setUp(self):
        self.base = '/var/www/html'
        self.collapse_map_before = {'forward': {}, 'reverse': {}}
        self.collapse_map_after = {
            'forward': {
                '2000/01/01/foo/index.html': 'foo-20000101.html'},
            'reverse': {
                'foo-20000101.html': '2000/01/01/foo/index.html'},
            }
        self.object_paths = {self.base: ['2000/01/01/foo/index.html']}

    def testCollapse(self):
        import parse2plone
        self.assertEqual(self.collapse_map_after,
            parse2plone.collapse_parts(
                self.object_paths,
                self.collapse_map_before,
                self.base))


# Test logger
class LoggerTestCase(unittest.TestCase):

    def setUp(self):
        import logging
        self.test_logger = logging.getLogger("test_logger")
        self.test_logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        outfile = logging.FileHandler(filename='test_logger.log')
        handler.setLevel(logging.INFO)
        outfile.setLevel(logging.INFO)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        self.test_logger.addHandler(handler)
        self.test_logger.addHandler(outfile)

    def testLogger(self):
        import parse2plone
        logger = parse2plone._setup_logger()
        self.assertTrue(isinstance(logger, self.test_logger.__class__))


# Test utils
class FakeLiteralEvalTestCase(unittest.TestCase):

    def setUp(self):
        import parse2plone
        self.utils = parse2plone.Utils()

    def testFakeLiteralEvalTrue(self):
        utils = self.utils
        self.assertEqual(True, utils._fake_literal_eval('True'))

    def testFakeLiteralEvalFalse(self):
        utils = self.utils
        self.assertEqual(False, utils._fake_literal_eval('False'))

    def testFakeLiteralEvalNone(self):
        utils = self.utils
        self.assertEqual(None, utils._fake_literal_eval('None'))

    def testFakeLiteralEvalMalformedString(self):
        utils = self.utils
        self.assertEqual((ValueError, 'malformed string'),
            utils._fake_literal_eval('asdf'))


class CleanPathTestCase(unittest.TestCase):

    def setUp(self):
        import parse2plone
        self.utils = parse2plone.Utils()

    def testCleanPath(self):
        utils = self.utils
        self.assertEqual('foo/bar/baz', utils._clean_path(
            '/foo/bar/baz/'))


class CheckExistsObjTestCase(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        import parse2plone
        self.utils = parse2plone.Utils()
        self.app = self.utils._setup_app(self.app)
        self.portal.invokeFactory('Folder', 'foo')

    def testCheckExistsObjTrue(self):
        self.assertTrue(self.utils._check_exists_obj(self.portal, 'foo'))

    def testCheckExistsObjFalse(self):
        self.assertFalse(self.utils._check_exists_obj(self.portal, 'qux'))


class CheckExistsPathTestCase(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        import parse2plone
        self.utils = parse2plone.Utils()
        self.path = 'plone/foo'
        self.app = self.utils._setup_app(self.app)
        self.portal.invokeFactory('Folder', 'foo')

    def testCheckExistsPathTrue(self):
        path = self.path
        self.assertTrue(self.utils._check_exists_path(self.app, path))


class ConvertStrToCSVTestCase(unittest.TestCase):

    def setUp(self):
        import parse2plone
        self.utils = parse2plone.Utils()
        self.value_before = '\nfoo bar\nbaz qux'
        self.value_after = 'foo:bar,baz:qux'

    def testConvertStrToCSV(self):
        utils = self.utils
        before = self.value_before
        after = self.value_after
        self.assertEqual(after, utils._convert_str_to_csv(before))


class ConvertCSVToListTestCase(unittest.TestCase):
    def setUp(self):
        import parse2plone
        self.utils = parse2plone.Utils()

        self.path_before = '/Plone'
        self.illegal_chars_before = '_,.'
        self.html_extensions_before = 'html'
        self.image_extensions_before = 'gif,jpg,jpeg,png'
        self.file_extensions_before = 'mp3'
        self.target_tags_before = 'a,div,h1,h2,p'
        self.force_before = False
        self.publish_before = False
        self.collapse_before = False
        self.rename_before = 'foo:bar,baz:qux'
        self.replacetypes_before = 'Document:MyDocument,Folder:MyFolder'
        self.match_before = '2000'
        self.paths_before = 'sample:/Plone/sample,sample2:/Plone/sample2'

        self.path_after = '/Plone'
        self.illegal_chars_after = ['_', '.']
        self.html_extensions_after = ['html']
        self.image_extensions_after = ['gif', 'jpg', 'jpeg', 'png']
        self.file_extensions_after = ['mp3']
        self.target_tags_after = ['a', 'div', 'h1', 'h2', 'p']
        self.force_after = False
        self.publish_after = False
        self.collapse_after = False
        self.rename_after = ['foo:bar', 'baz:qux']
        self.replacetypes_after = ['Document:MyDocument', 'Folder:MyFolder']
        self.match_after = ['2000']
        self.paths_after = 'sample:/Plone/sample,sample2:/Plone/sample2'

    def testConvertCSVToList(self):
        utils = self.utils

        path_before = self.path_before
        illegal_chars_before = self.illegal_chars_before
        html_extensions_before = self.html_extensions_before
        image_extensions_before = self.image_extensions_before
        file_extensions_before = self.file_extensions_before
        target_tags_before = self.target_tags_before
        force_before = self.force_before
        publish_before = self.publish_before
        collapse_before = self.collapse_before
        rename_before = self.rename_before
        replacetypes_before = self.replacetypes_before
        match_before = self.match_before
        paths_before = self.paths_before

        (illegal_chars, html_extensions, image_extensions, file_extensions,
        target_tags, path, force, publish, collapse, rename, replacetypes,
        match, paths) = (
            utils._convert_csv_to_list(illegal_chars_before,
            html_extensions_before, image_extensions_before,
            file_extensions_before, target_tags_before, path_before,
            force_before, publish_before, collapse_before, rename_before,
            replacetypes_before, match_before, paths_before))

        self.assertEqual(path, self.path_after)
        self.assertEqual(illegal_chars, self.illegal_chars_after)
        self.assertEqual(html_extensions, self.html_extensions_after)
        self.assertEqual(image_extensions, self.image_extensions_after)
        self.assertEqual(file_extensions, self.file_extensions_after)
        self.assertEqual(target_tags, self.target_tags_after)
        self.assertEqual(force, self.force_after)
        self.assertEqual(publish, self.publish_after)
        self.assertEqual(collapse, self.collapse_after)
        self.assertEqual(rename, self.rename_after)
        self.assertEqual(replacetypes, self.replacetypes_after)
        self.assertEqual(match, self.match_after)
        self.assertEqual(paths, self.paths_after)


class CreateOptionParserTestCase(unittest.TestCase):

    def setUp(self):
        import optparse
        import parse2plone

        _UNSET_OPTION = ''
        self.utils = parse2plone.Utils()

        self.option_parser_test = optparse.OptionParser()
        self.option_parser_test.add_option('-p', '--path',
            default=_UNSET_OPTION,
            dest='path',
            help='Path to Plone site object or sub-folder')
        self.option_parser_test.add_option('--html-extensions',
            default=_UNSET_OPTION,
            dest='html_extensions',
            help='Specify HTML file extensions')
        self.option_parser_test.add_option('--illegal-chars',
            default=_UNSET_OPTION,
            dest='illegal_chars',
            help='Specify characters to ignore')
        self.option_parser_test.add_option('--image-extensions',
            default=_UNSET_OPTION,
            dest='image_extensions',
            help='Specify image file extensions')
        self.option_parser_test.add_option('--file-extensions',
            default=_UNSET_OPTION,
            dest='file_extensions',
            help='Specify generic file extensions')
        self.option_parser_test.add_option('--target-tags',
            default=_UNSET_OPTION,
            dest='target_tags',
            help='Specify HTML tags to parse')
        self.option_parser_test.add_option('--force',
            action='store_true',
            default=_UNSET_OPTION,
            dest='force',
            help='Force creation of folders')
        self.option_parser_test.add_option('--publish',
            action='store_true',
            default=_UNSET_OPTION,
            dest='publish',
            help='Optionally publish newly created content')
        self.option_parser_test.add_option('--collapse',
            action='store_true',
            default=_UNSET_OPTION,
            dest='collapse',
            help="""Optionally "collapse" content (see collapse_parts())""")
        self.option_parser_test.add_option('--rename',
            default=_UNSET_OPTION,
            dest='rename',
            help='Optionally rename content (see rename_parts())')
        self.option_parser_test.add_option('--replacetypes',
            default=_UNSET_OPTION,
            dest='replacetypes',
            help='Optionally use custom content types (see replace types())')
        self.option_parser_test.add_option('--match',
            default=_UNSET_OPTION,
            dest='match',
            help='Only import content that matches PATTERN (see match_files())'
            )
        self.option_parser_test.add_option('--paths',
            default=_UNSET_OPTION,
            dest='paths',
            help='Specify import_dirs:object_paths (--path will be ignored)')

    def testCreateOptionParser(self):
        utils = self.utils
        option_parser_test = self.option_parser_test
        option_parser = utils._create_option_parser()
        # Make sure all the opts are the same e.g. '-p/--path'
        self.assertEqual(
            [i.__str__() for i in option_parser_test.option_list],
            [i.__str__() for i in option_parser.option_list])


class GetResultsTestCase(unittest.TestCase):

    def setUp(self):
        import parse2plone
        self.utils = parse2plone.Utils()
        self.results_0 = "'sample,sample2'"
        self.results_1 = "'/Plone/sample,/Plone/sample2'"
        self.paths_map = ['sample:/Plone/sample', 'sample2:/Plone/sample2']

    def testGetResults(self):
        utils = self.utils
        results_0 = self.results_0
        results_1 = self.results_1
        paths_map = self.paths_map
        self.assertEqual(results_0, utils._get_results(paths_map, 0))
        self.assertEqual(results_1, utils._get_results(paths_map, 1))


class ConvertObjToPathTestCase(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        import parse2plone
        self.utils = parse2plone.Utils()
        self.app = self.utils._setup_app(self.app)
        self.portal.invokeFactory('Folder', 'foo')
        self.obj = self.portal.foo
        self.results = '/plone/foo'

    def testConvertObjToPath(self):
        results = self.results
        utils = self.utils
        obj = self.obj
        self.assertEqual(results, utils._convert_obj_to_path(obj))


class RemoveBaseTestCase(unittest.TestCase):

    def setUp(self):
        import parse2plone
        self.utils = parse2plone.Utils()
        self.import_dir = 'sample'
        self.num_parts = len((self.import_dir).split('/'))
        self.files = ['sample/index.html', 'sample/2000/01/01/foo/index.html',
            'sample/_illegal_directory/index.html', 'sample/about/index.html',
            'sample/baz/index.html', 'sample/foo/index.html']

        self.results = {self.import_dir: ['index.html',
            '2000/01/01/foo/index.html', '_illegal_directory/index.html',
            'about/index.html', 'baz/index.html', 'foo/index.html']}

    def testRemoveBase(self):
        utils = self.utils
        import_dir = self.import_dir
        num_parts = self.num_parts
        files = self.files
        results = self.results
        self.assertEqual(results, utils._remove_base(files, num_parts,
            import_dir))


class GetFilesTestCase(unittest.TestCase):

    def setUp(self):
        import parse2plone

        self.utils = parse2plone.Utils()

        # Tests run in parts/test
        self.import_dir = '../../sample'

        self.results = ['../../sample/index.html',
            '../../sample/2000/01/01/foo/index.html',
            '../../sample/about/index.html', '../../sample/baz/index.html',
            '../../sample/foo/index.html']

    def testRemoveBase(self):
        utils = self.utils
        import_dir = self.import_dir
        results = self.results
        self.assertEqual(results, utils._get_files(import_dir))


class GetObjTestCase(unittest.TestCase):

    def setUp(self):
        import parse2plone
        self.path = '../../sample/foo'
        self.obj = 'foo'
        self.utils = parse2plone.Utils()

    def testGetObj(self):
        path = self.path
        obj = self.obj
        utils = self.utils
        self.assertEqual(obj, utils._get_obj(path))

class UpdateParentTestCase(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        import parse2plone
        self.utils = parse2plone.Utils()
        self.app = self.utils._setup_app(self.app)
        self.portal.invokeFactory('Folder', 'foo')
        self.obj = self.portal.foo
        self.parent_path = '/plone/foo/'

    def testUpdateParent(self):
        utils = self.utils
        obj = self.obj
        app = self.app
        parent_path = self.parent_path
        self.assertEqual(self.obj, utils._update_parent(self.portal, parent_path))

class GetPartsTestCase(unittest.TestCase):

    def setUp(self):
        import parse2plone
        self.utils = parse2plone.Utils()
        self.path = '/foo/bar/baz'
        self.results = ['foo','bar','baz']

    def testGetParts(self):
        path = self.path
        utils = self.utils
        results = self.results
        self.assertEqual(results, utils._get_parts(path))


class GetParentPathTestCase(unittest.TestCase):

    def setUp(self):
        import parse2plone
        self.utils = parse2plone.Utils()
        self.path = '/foo/bar/baz'
        self.parent_path = '/foo/bar'

    def testGetParts(self):
        path = self.path
        utils = self.utils
        parent_path = self.parent_path
        self.assertEqual(results, utils._get_parent_path(path))


# Test parse2plone

if __name__ == '__main__':
    unittest.main()
