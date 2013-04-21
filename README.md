ECoXiPy - Easy Creation of XML in Python
========================================

This Python project allows for easy creation of [XML](http://www.w3.org/XML/).
The hierarchical structure of XML is easy to spot and the code to create XML
is much shorter than using SAX, DOM or similar APIs.


<!--
## Getting Started

Install using [setuptools](https://pypi.python.org/pypi/setuptools):

    easy_install ecoxipy


You might also be interested in:

* [ECoXiPy on PyPi](https://pypi.python.org/pypi/ECoXiPy)
* [ECoXiPy Documentation](http://pythonhosted.org/ECoXiPy/)

-->

## Development

You should have [TinkerPy](https://github.com/IvIePhisto/TinkerPy) installed.


### Common Tasks

Install egg for development:

    python setup.py develop

Build documentation:

    python setup.py build_sphinx

Execute unit tests:

    python setup.py test


### Performance Testing

The performance tests create (nearly) the same HTML document in form of an
UTF-8 encoded string using different APIs. All supplied `ecoxipy.Output`
implementations (in `ecoxipy.string_output`, `ecoxipy.dom_output` and
`ecoxipy.element_output`) are tested as well as `xml.sax` and
`xml.dom.minidom` for comparison.

The output as an UTF-8 encoded string was chosen as most XML will ultimately
be serialised in this form. These tests show that `ecoxipy.string_output` is
faster than all others, followed by `xml.sax`, `xml.dom.minidom`,
`ecoxipy.dom_output` with `ecoxipy.element_output` at the end. Run the tests
your own or see the testing results in the repository under
`doc/perf_test_results`.

![Performance Test Results Graph](https://raw.github.com/IvIePhisto/ECoXiPy/master/doc/perf_test_results/timeit.png)

Run [timeit](http://docs.python.org/2/library/timeit.html) tests (linear
increase of `data_count` yields exponential test document size increase):

    python tests/performance/timeit_tests.py [<repetitions> <data count> [<CSV output path>]]


Run [cProfile](http://docs.python.org/2/library/profile.html) tests:

    python tests/performance/profiling_tests.py
