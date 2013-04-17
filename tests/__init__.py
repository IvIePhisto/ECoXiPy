import unittest, doctest
import ecoxipy
import ecoxipy.dom_output
import ecoxipy.element_output
import ecoxipy.string_output
import ecoxipy.html


class ECoXiPyTests(unittest.TestCase):
    def test_base(self):
        doctest.testmod(ecoxipy)

    def test_dom(self):
        doctest.testmod(ecoxipy.dom_output)

    def test_element(self):
        doctest.testmod(ecoxipy.element_output)

    def test_string(self):
        doctest.testmod(ecoxipy.string_output)

    def test_html(self):
        doctest.testmod(ecoxipy.html)


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(ECoXiPyTests)
    unittest.TextTestRunner(verbosity=2).run(suite)
