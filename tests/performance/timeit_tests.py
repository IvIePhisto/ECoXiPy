import sys
import platform
import timeit

from tests.performance import xml_sax
from tests.performance import xml_dom_minidom
from tests.performance import ecoxipy_pyxom_output
from tests.performance import ecoxipy_string_output
from tests.performance import ecoxipy_dom_output

LOREM_IPSUM = u'Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.'

if __name__ == '__main__':
    if len(sys.argv) not in (4, 5):
        print('''\
arguments: <string output> <repetitions> <data_count> [<file path>]

<string output>     If this is `true`, a byte string will be created.

<repetitions>       Specifies how often the tests should be run by `timeit`.

<data count>        Determines the length of the document, a linear increase
                    of this value yields exponential test document size
                    increase.

<CSV output path>   If this argument is given, the results are writen to a
                    file of this name as a comma separated table. Otherwise
                    the results are printed to the console.
''')
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
        "{0}.create_testdoc{2}(u'Test Page', u'Hello World!', {1}, u'{3}')".format(
            module.__name__, data_count, method_postfix, LOREM_IPSUM)
    )
    create_test_setup = lambda module: (
        "import {0}; {0}.create_testdoc{2}(u'startup', u'startup', {1}, u'{3}')".format(
            module.__name__, data_count, method_postfix, LOREM_IPSUM)
    )
    timeit_run = lambda module: timeit.timeit(
        create_test_run(module),
        setup=create_test_setup(module),
        number=repetitions)
    sax_time = timeit_run(xml_sax)
    dom_time = timeit_run(xml_dom_minidom)
    element_out_time = timeit_run(ecoxipy_pyxom_output)
    string_out_time = timeit_run(ecoxipy_string_output)
    dom_out_time = timeit_run(ecoxipy_dom_output)
    python_version = platform.python_version()
    python_platform = platform.python_implementation()
    try:
        pypy_version_info = sys.pypy_version_info
    except AttributeError:
        pass
    else:
        python_platform = '{} {}.{}.{}'.format(python_platform,
            pypy_version_info.major, pypy_version_info.minor,
            pypy_version_info.micro)
    output_name = 'Bytes' if string_output else 'Native'
    if len(sys.argv) < 5:
        min_time = min(sax_time, dom_time, element_out_time, string_out_time, dom_out_time)
        max_time = max(sax_time, dom_time, element_out_time, string_out_time, dom_out_time)
        create_percent = lambda t: '| {: >6.3f} secs | {: >6.3f} secs ({: >6.2f} %) |'.format(
            t, t-min_time, (t-min_time)/(max_time-min_time)*100)
        print('''\
# ECoXiPy Performance Tests

Python:                  Version {} on {}
Output:                  {}
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
| ecoxipy.pyxom.output   {}
| ecoxipy.string_output  {}\
'''.format(
            python_version, python_platform,
            output_name, repetitions, data_count,
            min_time, max_time, max_time - min_time,
            create_percent(sax_time),
            create_percent(dom_time),
            create_percent(dom_out_time),
            create_percent(element_out_time),
            create_percent(string_out_time),
        ))
    else:
        path = sys.argv[4]
        import os.path
        if not os.path.isfile(path):
            with open(path, 'w') as f:
                f.write('Output,Python Platform,Python Version,xml.sax,xml.dom.minidom,ecoxipy.dom_output,ecoxipy.pyxom.output,ecoxipy.string_output,Repetitions,Data Count\n')
        with open(path, 'a') as f:
            f.write('{},{},{},{},{},{},{},{},{},{}\n'.format(
                output_name, python_platform, python_version,
                sax_time, dom_time, dom_out_time, element_out_time,
                string_out_time, repetitions, data_count))
