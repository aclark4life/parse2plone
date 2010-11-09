import parse2plone
import unittest

from zc.buildout import testing


class Parse2PloneTestCase(unittest.TestCase):

    def setUp(self):
        pass

    def testFakeLiteralEvalTrue(self):
        self.assertEqual(True, parse2plone.fake_literal_eval('True'))

    def testFakeLiteralEvalFalse(self):
        self.assertEqual(False, parse2plone.fake_literal_eval('False'))

    def testFakeLiteralEvalNone(self):
        self.assertEqual(None, parse2plone.fake_literal_eval('None'))

    def testFakeLiteralEvalMalformedString(self):
        self.assertEqual((ValueError, 'malformed string'),
            parse2plone.fake_literal_eval('asdf'))

if __name__ == '__main__':
    unittest.main()
