ECoXiPy - Easy Creation of XML in Python
========================================

This Python project allows for easy creation of [XML](http://www.w3.org/XML/).
The hierarchical structure of XML is easy to spot and the code to create XML
is much shorter than using SAX, DOM or similar APIs.


## Getting Started

Install using [setuptools](https://pypi.python.org/pypi/setuptools):

    easy_install ecoxipy


You might also be interested in:

* [ECoXiPy on PyPi](https://pypi.python.org/pypi/ECoXiPy)
* [ECoXiPy Documentation](http://pythonhosted.org/ECoXiPy/)


## Development

Install egg for development:

    python setup.py develop


Build documentation:

    python setup.py build_sphinx


### Testing

These tests require [TinkerPy](https://github.com/IvIePhisto/TinkerPy) to
be installed.


Execute unit tests:

    python setup.py test


Run [timeit](http://docs.python.org/2/library/timeit.html) tests (linear
increase of `data_count` yields exponential test document size increase):

    python tests/performance/timeit_tests.py [<repetitions> <data count> [<CSV output path>]]


Run [cProfile](http://docs.python.org/2/library/profile.html) tests:

    python tests/performance/profiling_tests.py
