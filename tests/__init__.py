def test_suite():
    import unittest, doctest
    import ecoxipy
    import ecoxipy.dom_output
    import ecoxipy.element_output
    import ecoxipy.string_output
    import ecoxipy.html
    suite = unittest.TestSuite()
    suite.addTests(doctest.DocTestSuite(ecoxipy))
    suite.addTests(doctest.DocTestSuite(ecoxipy.dom_output))
    suite.addTests(doctest.DocTestSuite(ecoxipy.element_output))
    suite.addTests(doctest.DocTestSuite(ecoxipy.string_output))
    suite.addTests(doctest.DocTestSuite(ecoxipy.html))
    return suite
