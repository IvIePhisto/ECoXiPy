ECoXiPy - Easy Creation of XML in Python
========================================

This Python project allows for easy creation of [XML](http://www.w3.org/XML/).
The hierarchical structure of XML is easy to spot and the code to create XML
is much shorter than using SAX, DOM or similar APIs.

Here's a simple HTML5 document template function:

```python
# Import decorator to create HTML5 using "ecoxipy.MarkupBuilder" with
# "ecoxipy.string_output.StringOutput":
from ecoxipy.decorators import html5

@html5
def create_testdoc(_title, _subtitle, *_content):
    # The MarkupBuilder instance is available as "_b". Calling it embeds the
    # arguments, strings are regarded as raw XML:
    return _b(
        '<!DOCTYPE html>',                            # raw XML
        html(
            head(
                title(
                    # Explicitly create text node:
                    _b & _title
                )
            ),
            body(
                # Iterables and generators are unpacked automatically:
                [h1(_title), h2(_subtitle)],          # Iterable, e.g. a List
                (p(_item) for _item in _content),     # Generator

                # Callables are executed:
                hr,

                _b('<footer>Copyright 2013</footer>') # raw XML
            ),
            xmlns='http://www.w3.org/1999/xhtml/'
        )
    )
```

It could be used like this:

```python
>>> create_testdoc('Test', 'A Simple Test Document', 'Hello World & Universe!', 'How are you?')
'<!DOCTYPE html><html xmlns="http://www.w3.org/1999/xhtml/"><head><title>Test</title></head><body><h1>Test</h1><h2>A Simple Test Document</h2><p>Hello World &amp; Universe!</p><p>How are you?</p><hr/><footer>Copyright 2013</footer></body></html>'
```

Pretty-printing the result yields the following HTML:

```HTML
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml/">
    <head>
        <title>Test</title>
    </head>
    <body>
        <h1>Test</h1>
        <h2>A Simple Test Document</h2>
        <p>Hello World &amp; Universe!</p>
        <p>How are you?</p>
        <hr/>
        <footer>Copyright 2013</footer>
    </body>
</html>
```


## Getting Started

Install using [setuptools](https://pypi.python.org/pypi/setuptools):

    easy_install ecoxipy


You might also be interested in:

* [ECoXiPy on PyPi](https://pypi.python.org/pypi/ECoXiPy)
* [ECoXiPy Documentation](http://pythonhosted.org/ECoXiPy/)


## Release History

**0.2.0**
* *Added:* Use `&` on `ecoxipy.MarkupBuilder` to create text nodes.
* *Improvement:* Better performance of `ecoxipy.string_output.StringOutput`.


**0.1.0**
* *Initial release.*


## Development

Install egg for development:

    python setup.py develop


This installs [TinkerPy](https://github.com/IvIePhisto/TinkerPy), if you omit
it you must install TinkerPy manually.


### Common Tasks

Build documentation with [Sphinx](http://sphinx-doc.org) (which of course
must be installed):

    python setup.py build_sphinx

Execute unit tests:

    python setup.py test


### Performance Tests

The performance tests create (nearly) the same HTML document in form of an
UTF-8 encoded string using different APIs. The output as an UTF-8 encoded
string was chosen as most XML will ultimately be serialised in this form. All
supplied `ecoxipy.Output` implementations (in `ecoxipy.string_output`,
`ecoxipy.dom_output` and `ecoxipy.element_output`) are tested as well as
`xml.sax` and `xml.dom.minidom` for comparison.


Run [timeit](http://docs.python.org/2/library/timeit.html) tests (linear
increase of `data_count` yields exponential test document size increase):

    python tests/performance/timeit_tests.py [<repetitions> <data count> [<CSV output path>]]


To create a CSV file from a series of tests in Bash as I did for my
performance test results:

    for ((i = 2; i <= 20; i += 2)); do python tests/performance/timeit_tests.py 400 $i timeit.csv; done


Run [cProfile](http://docs.python.org/2/library/profile.html) tests:

    python tests/performance/profiling_tests.py


These tests show that `ecoxipy.string_output` is faster than all others,
followed by `xml.sax`, `ecoxipy.element_output`, `xml.dom.minidom` with
`ecoxipy.dom_output` at the end. Run the tests on your own or see my testing
results in the repository under
[doc/perf_test_results/timeit.pdf](https://raw.github.com/IvIePhisto/ECoXiPy/master/doc/perf_test_results/timeit.pdf).

![Performance Testing Results Graph](https://raw.github.com/IvIePhisto/ECoXiPy/master/doc/perf_test_results/timeit.png)
