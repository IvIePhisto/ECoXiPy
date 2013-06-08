def test_suite():
    import unittest, doctest
    import ecoxipy
    import ecoxipy.dom_output
    import ecoxipy.string_output
    import ecoxipy.etree_output
    import ecoxipy.pyxom
    import ecoxipy.pyxom._document
    import ecoxipy.pyxom.output
    import ecoxipy.pyxom.indexing
    import ecoxipy.decorators
    import ecoxipy.parsing
    suite = unittest.TestSuite()
    suite.addTests(doctest.DocTestSuite(ecoxipy))
    suite.addTests(doctest.DocTestSuite(ecoxipy.dom_output))
    suite.addTests(doctest.DocTestSuite(ecoxipy.etree_output))
    suite.addTests(doctest.DocTestSuite(ecoxipy.string_output))
    suite.addTests(doctest.DocTestSuite(ecoxipy.pyxom))
    suite.addTests(doctest.DocTestSuite(ecoxipy.pyxom._document))
    suite.addTests(doctest.DocTestSuite(ecoxipy.pyxom.output))
    suite.addTests(doctest.DocTestSuite(ecoxipy.pyxom.indexing))
    suite.addTests(doctest.DocTestSuite(ecoxipy.decorators))
    suite.addTests(doctest.DocTestSuite(ecoxipy.parsing))
    return suite
