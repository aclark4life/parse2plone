import unittest

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(TestCase('foo'))
    suite.addTest(TestCase('bar'))
    suite.addTest(TestCase('bar'))
    return suite

class TestCase(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def foo(self):
        pass

    def bar(self):
        pass

    def baz(self):
        pass
