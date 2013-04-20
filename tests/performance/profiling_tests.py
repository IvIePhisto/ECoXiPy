import cProfile

import ecoxipy_element_output
import ecoxipy_string_output


create_test_run = lambda module: "for i in xrange(1000): {}.create_testdoc('Test Page', 'Hello World!')".format(module.__name__)
create_test_setup = lambda module: "from __main__ import {0}; print {0}.create_testdoc('startup', 'startup')".format(module.__name__)

if __name__ == '__main__':
    print '''
    ECoXiPy Profiling
    =================

    ecoxipy.element_output
    ----------------------
    '''
    cProfile.run(create_test_run(ecoxipy_element_output), sort='tottime')

    print '''
    ecoxipy.string_output
    ---------------------
    '''
    cProfile.run(create_test_run(ecoxipy_string_output), sort='tottime')
