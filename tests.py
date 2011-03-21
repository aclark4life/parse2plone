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
        self.recipe_input_after = ['\n/foo,/bar', '\n/baz,/qux']

    def testRenameOldNew(self):
        import charm as parse2plone
        rename_map_before = self.rename_map_before
        rename_map_after = self.rename_map_after
        files = self.files
        base = self.base
        rename = ['foo:bar', 'baz:qux']
        self.assertEqual(rename_map_after,
            parse2plone.rename_parts(
            files, rename_map_before, base, rename))

    def testConvertRecipeInputToCSV(self):
        import charm as parse2plone
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
        import charm as parse2plone
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
        import charm as parse2plone
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
        import charm as parse2plone
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
        import charm as parse2plone
        logger = parse2plone._setup_logger()
        self.assertTrue(isinstance(logger, self.test_logger.__class__))


# Test utils
class FakeLiteralEvalTestCase(unittest.TestCase):

    def setUp(self):
        import charm as parse2plone
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
        import charm as parse2plone
        self.utils = parse2plone.Utils()

    def testCleanPath(self):
        utils = self.utils
        self.assertEqual('foo/bar/baz', utils._clean_path(
            '/foo/bar/baz/'))


class CheckExistsObjTestCase(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        import charm as parse2plone
        from AccessControl.SecurityManagement import newSecurityManager
        from AccessControl.SpecialUsers import system
        from Testing.makerequest import makerequest
        self.app = makerequest(self.app)
        newSecurityManager(None, system)
        self.utils = parse2plone.Utils()
        self.portal.invokeFactory('Folder', 'foo')

    def testCheckExistsObjTrue(self):
        self.assertTrue(self.utils._check_exists_obj(self.portal, 'foo'))

    def testCheckExistsObjFalse(self):
        self.assertFalse(self.utils._check_exists_obj(self.portal, 'qux'))


class CheckExistsPathTestCase(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        import charm as parse2plone
        from AccessControl.SecurityManagement import newSecurityManager
        from AccessControl.SpecialUsers import system
        from Testing.makerequest import makerequest
        self.app = makerequest(self.app)
        newSecurityManager(None, system)
        self.utils = parse2plone.Utils()
        self.path = 'plone/foo'
        self.portal.invokeFactory('Folder', 'foo')

    def testCheckExistsPathTrue(self):
        path = self.path
        self.assertTrue(self.utils._check_exists_path(self.app, path))


class ConvertStrToCSVTestCase(unittest.TestCase):

    def setUp(self):
        import charm as parse2plone
        self.utils = parse2plone.Utils()
        self.value_before = '\nfoo bar\nbaz qux'
        self.value_after = '\nfoo,bar\nbaz,qux'

    def testConvertStrToCSV(self):
        utils = self.utils
        before = self.value_before
        after = self.value_after
        self.assertEqual(after, utils._convert_str_to_csv(before))


class ConvertObjToPathTestCase(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        import charm as parse2plone
        from AccessControl.SecurityManagement import newSecurityManager
        from AccessControl.SpecialUsers import system
        from Testing.makerequest import makerequest
        self.app = makerequest(self.app)
        newSecurityManager(None, system)
        self.utils = parse2plone.Utils()
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
        import charm as parse2plone
        self.utils = parse2plone.Utils()
        self.import_dir = 'html'
        self.num_parts = len((self.import_dir).split('/'))
        self.files = ['html/index.html']
        self.results = {self.import_dir: ['index.html']}

    def testRemoveBase(self):
        utils = self.utils
        import_dir = self.import_dir
        num_parts = self.num_parts
        files = self.files
        results = self.results
        self.assertEqual(results, utils._remove_base(files, num_parts,
            import_dir))


class RemovePartsTestCase(unittest.TestCase):

    def setUp(self):
        import charm as parse2plone
        self.utils = parse2plone.Utils()
        self.parts_before = ['/var/www/html/foo']
        self.parts_after = [['foo']]

    def testRemoveParts(self):
        utils = self.utils
        before = self.parts_before
        after = self.parts_after
        self.assertEqual(after, utils._remove_parts(before, 3))


class GetObjTestCase(unittest.TestCase):

    def setUp(self):
        import charm as parse2plone
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
        import charm as parse2plone
        from AccessControl.SecurityManagement import newSecurityManager
        from AccessControl.SpecialUsers import system
        from Testing.makerequest import makerequest
        self.app = makerequest(self.app)
        newSecurityManager(None, system)
        self.utils = parse2plone.Utils()
        self.portal.invokeFactory('Folder', 'foo')
        self.obj = self.portal.foo
        self.parent_path = '/plone/foo/'

    def testUpdateParent(self):
        utils = self.utils
        parent_path = self.parent_path
        self.assertEqual(self.obj, utils._update_parent(self.portal,
            parent_path))


class GetPartsTestCase(unittest.TestCase):

    def setUp(self):
        import charm as parse2plone
        self.utils = parse2plone.Utils()
        self.path = '/foo/bar/baz'
        self.results = ['foo', 'bar', 'baz']

    def testGetParts(self):
        path = self.path
        utils = self.utils
        results = self.results
        self.assertEqual(results, utils._get_parts(path))


class GetParentPartsTestCase(unittest.TestCase):

    def setUp(self):
        import charm as parse2plone
        self.utils = parse2plone.Utils()
        self.path = 'foo/bar/baz'
        self.parent_parts = ['foo', 'bar']

    def testGetParentParts(self):
        path = self.path
        utils = self.utils
        parent_parts = self.parent_parts
        self.assertEqual(parent_parts, utils._get_parent_parts(path))


class IsFileTestCase(unittest.TestCase):

    def setUp(self):
        import charm as parse2plone
        self.utils = parse2plone.Utils()
        self.html_file = 'index.html'
        self.image_file = 'foo.png'
        self.file = 'foo.mp3'
        self.html_extensions = ['html']
        self.image_extensions = ['png']
        self.file_extensions = ['mp3']

    def testIsHTMLFile(self):
        file = self.html_file
        utils = self.utils
        extensions = self.html_extensions
        self.assertTrue(utils._is_file(file, extensions))

    def testIsImageFile(self):
        file = self.image_file
        utils = self.utils
        extensions = self.image_extensions
        self.assertTrue(utils._is_file(file, extensions))

    def testIsFile(self):
        file = self.file
        utils = self.utils
        extensions = self.file_extensions
        self.assertTrue(utils._is_file(file, extensions))


class IsFolderTestCase(unittest.TestCase):

    def setUp(self):
        import charm as parse2plone
        self.utils = parse2plone.Utils()
        self.folder_good = 'foo'
        self.folder_bad = 'foo.bar'

    def testIsFolderGood(self):
        utils = self.utils
        folder = self.folder_good
        self.assertTrue(utils._is_folder(folder))

    def testIsFolderBad(self):
        utils = self.utils
        folder = self.folder_bad
        self.assertFalse(utils._is_folder(folder))


class IsLegalTestCase(unittest.TestCase):

    def setUp(self):
        import charm as parse2plone
        self.utils = parse2plone.Utils()
        self.obj_good = 'foo'
        self.obj_bad = '_foo'

    def testIsLegalGood(self):
        utils = self.utils
        obj = self.obj_good
        self.assertTrue(utils._is_legal(obj))

    def testIsLegalBad(self):
        utils = self.utils
        obj = self.obj_bad
        self.assertFalse(utils._is_legal(obj))


class SetupAppTestCase(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        import charm as parse2plone
        self.utils = parse2plone.Utils()

    def testSetupApp(self):
        # If we are setup we can do this
        utils = self.utils
        from Products.CMFCore.exceptions import AccessControl_Unauthorized
        self.app = utils._setup_app(self.app)
        try:
            self.portal.invokeFactory('Folder', 'foo')
        except AccessControl_Unauthorized:
            self.fail()


class ValidateRecipeArgsTestCase(unittest.TestCase):

    def setUp(self):
        import charm as parse2plone
        self.utils = parse2plone.Utils()
        self.options_good = ['path']
        self.options_bad = ['foo']

    def testValidateRecipeArgsGood(self):
        utils = self.utils
        options = self.options_good
        self.assertTrue(utils._validate_recipe_args(options))

    def testValidateRecipeArgsBad(self):
        utils = self.utils
        options = self.options_bad
        self.assertFalse(utils._validate_recipe_args(options))

# Test parse2plone

if __name__ == '__main__':
    unittest.main()
