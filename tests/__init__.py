def test_suite():
    import unittest, doctest
    import ecoxipy
    import ecoxipy.dom_output
    import ecoxipy.pyxom_output
    import ecoxipy.string_output
    import ecoxipy.decorators
    import ecoxipy.pyxom
    suite = unittest.TestSuite()
    suite.addTests(doctest.DocTestSuite(ecoxipy))
    suite.addTests(doctest.DocTestSuite(ecoxipy.string_output))
    suite.addTests(doctest.DocTestSuite(ecoxipy.pyxom))
    suite.addTests(doctest.DocTestSuite(ecoxipy.pyxom_output))
    suite.addTests(doctest.DocTestSuite(ecoxipy.dom_output))
    suite.addTests(doctest.DocTestSuite(ecoxipy.decorators))
    return suite
