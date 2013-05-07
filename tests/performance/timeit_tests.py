import sys
import timeit

import xml_sax
import xml_dom_minidom
import ecoxipy_element_output
import ecoxipy_string_output
import ecoxipy_dom_output


TIMEIT_NUMBER = 100
TIMEIT_DATA_COUNT = 10

if __name__ == '__main__':
    if 4 > len(sys.argv) > 5:
        print 'arguments: [<string output> <repetitions> <data_count> [<file path>]]'
        sys.exit(1)
    else:
        string_output = sys.argv[1].lower() == 'true'
        repetitions = int(sys.argv[2])
        data_count = int(sys.argv[3])
    if string_output:
        method_postfix = '_string'
    else:
        method_postfix = ''
    create_test_run = lambda module: (
        "{0}.create_testdoc{2}('Test Page', 'Hello World!', {1}, 'Lorem Ipsum')".format(
            module.__name__, data_count, method_postfix)
    )
    create_test_setup = lambda module: (
        "from __main__ import {0}; {0}.create_testdoc{2}('startup', 'startup', {1}, 'Lorem Ipsum')".format(
            module.__name__, data_count, method_postfix)
    )
    timeit_run = lambda module: timeit.timeit(
        create_test_run(module),
        setup=create_test_setup(module),
        number=repetitions)
    sax_time = timeit_run(xml_sax)
    dom_time = timeit_run(xml_dom_minidom)
    element_out_time = timeit_run(ecoxipy_element_output)
    string_out_time = timeit_run(ecoxipy_string_output)
    dom_out_time = timeit_run(ecoxipy_dom_output)
    if len(sys.argv) < 5:
        min_time = min(sax_time, dom_time, element_out_time, string_out_time, dom_out_time)
        max_time = max(sax_time, dom_time, element_out_time, string_out_time, dom_out_time)
        create_percent = lambda t: '| {: >6.3f} secs | {: >6.3f} secs ({: >6.2f} %) |'.format(
            t, t-min_time, (t-min_time)/(max_time-min_time)*100)
        print '''\
# ECoXiPy Performance Tests

String output:           {}
Number of repetitions:   {}
Number of data elements: {}

## Run Time Results

Minimum:    {: >6.3f} secs
Maximum:    {: >6.3f} secs
Difference: {: >6.3f} secs

Running Times:

| API                    | absolute    | relative               |
|------------------------|-------------|------------------------|
| xml.sax                {}
| xml.dom.minidom        {}
| ecoxipy.dom_output     {}
| ecoxipy.element_output {}
| ecoxipy.string_output  {}\
'''.format(
            string_output, repetitions, data_count,
            min_time, max_time, max_time - min_time,
            create_percent(sax_time),
            create_percent(dom_time),
            create_percent(dom_out_time),
            create_percent(element_out_time),
            create_percent(string_out_time),
        )
    else:
        path = sys.argv[3]
        import os.path
        if not os.path.isfile(path):
            with open(path, 'w') as f:
                f.write('Repetitions,Data Count,xml.sax,xml.dom.minidom,ecoxipy.dom_output,ecoxipy.element_output,ecoxipy.string_output\n')
        with open(path, 'a') as f:
            f.write('{},{},{},{},{},{},{}\n'.format(
                repetitions, data_count,
                sax_time, dom_time, dom_out_time, element_out_time,
                string_out_time))
