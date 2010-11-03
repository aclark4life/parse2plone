import unittest

from zc.buildout import testing

class ConfigOptionsTestCase(unittest.TestCase):

    def setUp(self):
        pass

    def testCustomPath(self):
        # The first thing we want to test is that if someone
        # customizes the path, their customization is saved in
        # the _SETTINGS dict (and used in Parse2Plone).
        pass

if __name__ == '__main__':
    unittest.main()
