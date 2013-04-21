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


### Testing

These tests require [TinkerPy](https://github.com/IvIePhisto/TinkerPy) to
be installed.


Execute unit tests:

    python setup.py test


Run `timeit` tests:

    python tests/performance/timeit_tests.py


Run `cProfile` tests:

    python tests/performance/profiling_tests.py