import cProfile
import sys

from tests.performance import ecoxipy_pyxom_output
from tests.performance import ecoxipy_string_output
from tests.performance import ecoxipy_dom_output
from tests.performance.timeit_tests import LOREM_IPSUM

TIMEIT_NUMBER, TIMEIT_DATA_COUNT = sys.argv[1:]

def create_test_run(module):
    format_str = '''\
import {0}
for i in xrange({1}):
    {0}.create_testdoc('Test Page', 'Hello World!', {2}, u'{3}')
'''
    return format_str.format(module.__name__, TIMEIT_NUMBER, TIMEIT_DATA_COUNT, LOREM_IPSUM)

if __name__ == '__main__':
    print '''
    ECoXiPy Profiling
    =================

    ecoxipy.pyxom.output
    ----------------------
    '''
    cProfile.run(create_test_run(ecoxipy_pyxom_output), sort='tottime')

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
