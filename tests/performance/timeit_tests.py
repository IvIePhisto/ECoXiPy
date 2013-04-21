import timeit

import xml_sax
import xml_dom_minidom
import ecoxipy_element_output
import ecoxipy_string_output
import ecoxipy_dom_output


TIMEIT_NUMBER = 200
TIMEIT_DATA_COUNT = 100

if __name__ == '__main__':
    create_test_run = lambda module: "{}.create_testdoc('Test Page', 'Hello World!', {})".format(module.__name__, TIMEIT_DATA_COUNT)
    create_test_setup = lambda module: "from __main__ import {0}; {0}.create_testdoc('startup', 'startup', {1})".format(module.__name__, TIMEIT_DATA_COUNT)
    create_percent = lambda t, m: '{: >6.2f} %'.format((t-m)/m*100)
    timeit_run = lambda module: timeit.timeit(
        create_test_run(module),
        setup=create_test_setup(module),
        number=TIMEIT_NUMBER)
    sax_time = timeit_run(xml_sax)
    dom_time = timeit_run(xml_dom_minidom)
    element_out_time = timeit_run(ecoxipy_element_output)
    string_out_time = timeit_run(ecoxipy_string_output)
    dom_out_time = timeit_run(ecoxipy_dom_output)
    min_time = min(sax_time, dom_time, element_out_time, string_out_time, dom_out_time)
    max_time = max(sax_time, dom_time, element_out_time, string_out_time, dom_out_time)

    print '''
ECoXiPy Performance Tests
=========================

Number of repetitions:      {}
Number of data elements:    {}

Minimum Time:           {}
Maximum Time:           {}

The individual APIs had a runtime increase in respect to the minimum time of:
xml.sax                 {}
xml.dom.minidom         {}
ecoxipy.dom_output      {}
ecoxipy.element_output  {}
ecoxipy.string_output   {}
'''.format(
        TIMEIT_NUMBER, TIMEIT_DATA_COUNT, min_time, max_time,
        create_percent(sax_time, min_time),
        create_percent(dom_time, min_time),
        create_percent(dom_out_time, min_time),
        create_percent(element_out_time, min_time),
        create_percent(string_out_time, min_time),
    )
