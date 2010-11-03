import unittest
import zc.buildout.testing

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(TestCase('test_path_input'))
    return suite

class TestCase(unittest.TestCase):

    def test_path_input(self):
        pass
