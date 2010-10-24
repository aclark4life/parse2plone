import unittest

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(TestCase('parse_args'))
    return suite

class TestCase(unittest.TestCase):

    def parse_args(self):
        pass
