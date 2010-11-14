import parse2plone
import unittest


# Test private function
class FakeLiteralEvalTestCase(unittest.TestCase):

    def testFakeLiteralEvalTrue(self):
        self.assertEqual(True, parse2plone._fake_literal_eval('True'))

    def testFakeLiteralEvalFalse(self):
        self.assertEqual(False, parse2plone._fake_literal_eval('False'))

    def testFakeLiteralEvalNone(self):
        self.assertEqual(None, parse2plone._fake_literal_eval('None'))

    def testFakeLiteralEvalMalformedString(self):
        self.assertEqual((ValueError, 'malformed string'),
            parse2plone._fake_literal_eval('asdf'))


# Test private function
class CleanPathTestCase(unittest.TestCase):

    def testCleanPath(self):
        self.assertEqual('foo/bar/baz', parse2plone._clean_path(
            '/foo/bar/baz/'))


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
        self.recipe_input_after = ['foo:bar', 'baz:qux']

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
        results = []
        recipe_input_before = self.recipe_input_before
        recipe_input_after = self.recipe_input_after

        for recipe_input in recipe_input_before:
            results.append(parse2plone._convert_paths_to_csv(recipe_input,
                'rename'))

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

if __name__ == '__main__':
    unittest.main()
