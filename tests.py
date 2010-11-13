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
            results.append(parse2plone._convert_paths_to_csv(recipe_input, 'rename'))

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


# Test "customtypes" feature
class CustomTypesTestCase(unittest.TestCase):

    def setUp(self):
        pass

    def testCustomTypes(self):
        pass


# Test "collapse" feature
class CollapseTestCase(unittest.TestCase):

    def setUp(self):
        pass

    def testCollapse(self):
        pass


if __name__ == '__main__':
    unittest.main()
