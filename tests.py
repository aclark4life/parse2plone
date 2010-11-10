import parse2plone
import unittest


class FakeLiteralEvalTestCase(unittest.TestCase):

    def testFakeLiteralEvalTrue(self):
        self.assertEqual(True, parse2plone.fake_literal_eval('True'))

    def testFakeLiteralEvalFalse(self):
        self.assertEqual(False, parse2plone.fake_literal_eval('False'))

    def testFakeLiteralEvalNone(self):
        self.assertEqual(None, parse2plone.fake_literal_eval('None'))

    def testFakeLiteralEvalMalformedString(self):
        self.assertEqual((ValueError, 'malformed string'),
            parse2plone.fake_literal_eval('asdf'))


class CleanPathTestCase(unittest.TestCase):

    def testCleanPath(self):
        self.assertEqual('foo/bar/baz', parse2plone.clean_path(
            '/foo/bar/baz/'))


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

    def testRenameOldNew(self):
        rename_map_before = self.rename_map_before
        rename_map_after = self.rename_map_after
        files = self.files
        base = self.base
        rename = ['foo:bar', 'baz:qux']
        self.assertEqual(rename_map_after,
            parse2plone.rename_old_to_new(
            files, rename_map_before, base, rename))


if __name__ == '__main__':
    unittest.main()
