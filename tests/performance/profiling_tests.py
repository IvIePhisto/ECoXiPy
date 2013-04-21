import cProfile

import ecoxipy_element_output
import ecoxipy_string_output
import ecoxipy_dom_output

from timeit_tests import TIMEIT_NUMBER, TIMEIT_DATA_COUNT

create_test_run = lambda module: "for i in xrange({1}): {0}.create_testdoc('Test Page', 'Hello World!', {2})".format(module.__name__, TIMEIT_NUMBER, TIMEIT_DATA_COUNT)

if __name__ == '__main__':
    print '''
    ECoXiPy Profiling
    =================

    ecoxipy.element_output
    ----------------------
    '''
    cProfile.run(create_test_run(ecoxipy_element_output), sort='tottime')

    print '''
    ecoxipy.dom_output
    ---------------------
    '''
    cProfile.run(create_test_run(ecoxipy_dom_output), sort='tottime')

    print '''
    ecoxipy.string_output
    ---------------------
    '''
    cProfile.run(create_test_run(ecoxipy_string_output), sort='tottime')