import parse2plone
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
        rename_map_before = self.rename_map_before
        rename_map_after = self.rename_map_after
        files = self.files
        base = self.base
        rename = ['foo:bar', 'baz:qux']
        self.assertEqual(rename_map_after,
            parse2plone.rename_parts(
            files, rename_map_before, base, rename))

    def testConvertRecipeInputToCSV(self):
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
        logger = parse2plone._setup_logger()
        self.assertTrue(isinstance(logger, self.test_logger.__class__))


# Test utils
class FakeLiteralEvalTestCase(unittest.TestCase):

    def setUp(self):
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
        self.utils = parse2plone.Utils()

    def testCleanPath(self):
        utils = self.utils
        self.assertEqual('foo/bar/baz', utils._clean_path(
            '/foo/bar/baz/'))


class CheckExistsObjTestCase(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.utils = parse2plone.Utils()
        self.app = self.utils._setup_app(self.app)
        self.portal.invokeFactory('Folder', 'foo')

    def testCheckExistsObjTrue(self):
        self.assertTrue(self.utils._check_exists_obj(self.portal, 'foo'))

    def testCheckExistsObjFalse(self):
        self.assertFalse(self.utils._check_exists_obj(self.portal, 'qux'))


class CheckExistsPathTestCase(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.utils = parse2plone.Utils()
        self.path = 'plone/foo'
        self.app = self.utils._setup_app(self.app)
        self.portal.invokeFactory('Folder', 'foo')

    def testCheckExistsPathTrue(self):
        path = self.path
        self.assertTrue(self.utils._check_exists_path(self.app, path))


class ConvertStrToCSVTestCase(unittest.TestCase):

    def setUp(self):
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
        self.rename_before ='foo:bar,baz:qux'
        self.replacetypes_before = 'Document:MyDocument,Folder:MyFolder'
        self.match_before = '2000'
        self.paths_before = 'sample:/Plone/sample,sample2:/Plone/sample2'

        self.path_after = '/Plone'
        self.illegal_chars_after = ['_','.']
        self.html_extensions_after = ['html']
        self.image_extensions_after = ['gif','jpg','jpeg','png']
        self.file_extensions_after = ['mp3']
        self.target_tags_after = ['a','div','h1','h2','p']
        self.force_after = False
        self.publish_after = False
        self.collapse_after = False
        self.rename_after = ['foo:bar','baz:qux']
        self.replacetypes_after = ['Document:MyDocument','Folder:MyFolder']
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

        path_after = self.path_after
        illegal_chars_after= self.illegal_chars_after
        html_extensions_after= self.html_extensions_after
        image_extensions_after= self.image_extensions_after
        file_extensions_after= self.file_extensions_after
        target_tags_after= self.target_tags_after
        force_after= self.force_after
        publish_after= self.publish_after
        collapse_after= self.collapse_after
        rename_after= self.rename_after
        replacetypes_after= self.replacetypes_after
        match_after= self.match_after
        paths_after= self.paths_after

        (illegal_chars, html_extensions, image_extensions, file_extensions,
        target_tags, path, force, publish, collapse, rename, replacetypes,
        match, paths) = (utils._convert_csv_to_list(illegal_chars_before,
        html_extensions_before, image_extensions_before, file_extensions_before,
        target_tags_before, path_before, force_before, publish_before,
        collapse_before, rename_before, replacetypes_before, match_before, paths_before))

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

# Test parse2plone


if __name__ == '__main__':
    unittest.main()
