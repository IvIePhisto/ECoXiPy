# ECoXiPy - Easy Creation of XML in Python

This Python 2 and 3 project (tested with CPython 2.7 and 3.3  as well as PyPy
2.0 and 2.1) allows for easy creation of [XML](http://www.w3.org/XML/). The
hierarchical structure of XML is easy to spot and the code to create XML
is much shorter than using SAX, DOM or similar APIs.

This project uses the MIT License, so you may freely use, distribute and
modify it, provided you include the content of `License.txt`.


## Getting Started

Install using [setuptools](https://pypi.python.org/pypi/setuptools) (only
Python 2) or [distribute](http://pythonhosted.org/distribute/):

    easy_install ecoxipy


You might also be interested in:

* [ECoXiPy on PyPi](https://pypi.python.org/pypi/ECoXiPy)
* [ECoXiPy Documentation](http://pythonhosted.org/ECoXiPy/)


## Release History

**0.3.1**

*   *Improved:* Performance – more duck-typing and less `isinstance`, using
    `collections.queue` instead of `list` for children handling.
*   *Fixed:* Text handling of `ecoxipy.etree_output.ETreeOutput`.
*   *Added:* Performance tests for `ecoxipy.etree_output.ETreeOutput`.

**0.3.0**

This is a major release introducing new capabilities and Python 3 support.

*   *Added:* Support for Python 3.
*   *Added:* Use `|` on `ecoxipy.MarkupBuilder` to create comments.
*   *Added:* Use slicing on `ecoxipy.MarkupBuilder` to create documents
    or processing instructions.
*   *Added:* The module `ecoxipy.parsing` contains SAX to ECoXiPy parsing
    facilities.
*   *Changed:* Renamed module `ecoxipy.element_output` to
    `ecoxipy.pyxom.output` and moved the XML representation classes to their
    own module `ecoxipy.pyxom` naming them *PyXOM* - **Pythonic XML Object
    Model** as well as adding new functionality. DOM creation was removed from
    those classes.
*   *Changed:* All XML data is internally handled as Unicode, a
    `ecoxipy.MarkupBuilder` instance converts byte strings from an encoding
    given on creation (defaults to UTF-8).
*   *Changed:* XML parsing is now handled by `ecoxipy.MarkupBuilder` instead
    of the `ecoxipy.Output` implementations.
*   *Changed:* Text node creation is now handled by `ecoxipy.MarkupBuilder`
    instead of the `ecoxipy.Output` implementations.
*   *Improved:* Unpacking of content while processing is done recursively on
    iterable and callable content.


**0.2.0**
*   *Added:* Use `&` on `ecoxipy.MarkupBuilder` to create text nodes.
*   *Improvement:* Better performance of `ecoxipy.string_output.StringOutput`.


**0.1.0**
*   *Initial release.*


## Example

Here's a simple HTML5 document template function:

```python
# In the function it is applied to the "html5" decorator creates the variable
# "_b" being an instance of "ecoxipy.MarkupBuilder" with
# "ecoxipy.string_output.StringOutput" for XML creation. It also creates for
# each HTML5 element a variable being a method of "_b", with the name of
# element, variable and method all being equal.

from ecoxipy.decorators import html5

@html5
def create_testdoc(title, subtitle, *content):
    # Slicing without start argument on the builder creates a document, the
    # stop argument defines the document type declaration and the step
    # argument defines if the XML declaration should be omitted.
    return _b[:'html':True](
        # Method calls on a MarkupBuilder instance create elements with the
        # name equal to the method name.
        html(
            # Child dictionary entries become attributes, especially useful
            # for non-identifier attribute names:
            {'data-info': 'Created by Ecoxipy'},
            head(
                _b.title(
                    # Children which are not of the XML representation
                    # and are either "str" or "unicode" instances or are
                    # neither iterables, generators nor callables, become text
                    # nodes:
                    title
                )
            ),
            body(
                article(
                    # Child iterables and generators are unpacked
                    # automatically:
                    [h1(title), h2(subtitle)],          # Iterable
                    (p(item) for item in content),      # Generator

                    # Child callables are executed:
                    hr,

                    # Calling a MarkupBuilder creates a XML fragment from the
                    # arguments, here strings are regarded as raw XML.
                    _b(
                        # Explicitly create text node:
                        _b & '<THE END>',
                        '<footer>Copyright 2013</footer>'       # raw XML
                    )
                )
            ),

            # You can also create comments:
            _b | "This is a comment.",

            # Slicing with a start argument creates a processing instruction:
            _b['pi-target':'PI content.'],

            # Named arguments of element method-calls become attributes:
            xmlns='http://www.w3.org/1999/xhtml/'
        )
    )
```


It could be used like this:

```python
>>> create_testdoc('Test', 'A Simple Test Document', 'Hello World & Universe!', 'How are you?')
b'<!DOCTYPE html><html data-info="Created by Ecoxipy" xmlns="http://www.w3.org/1999/xhtml/"><head><title>Test</title></head><body><article><h1>Test</h1><h2>A Simple Test Document</h2><p>Hello World &amp; Universe!</p><p>How are you?</p><hr/>&lt;THE END&gt;<footer>Copyright 2013</footer><!--This is a comment.--><?pi-target PI content.?></article></body></html>'
```

Pretty-printing the result yields the following HTML:

```HTML
<!DOCTYPE html>
<html data-info="Created by Ecoxipy" xmlns="http://www.w3.org/1999/xhtml/">
    <head>
        <title>Test</title>
    </head>
    <body>
        <article>
            <h1>Test</h1>
            <h2>A Simple Test Document</h2>
            <p>Hello World &amp; Universe!</p>
            <p>How are you?</p>
            <hr/>
            &lt;THE END&gt;
            <footer>Copyright 2013</footer>
        </article>
    </body>
    <!--This is a comment.-->
    <?pi-target PI content.?>
</html>
```


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

**Setup**

The same XHTML5 document is created with different APIs. All output
implementations of EcoXiPy (in `ecoxipy.string_output`, `ecoxipy.dom_output`
and `ecoxipy.pyxom.output`) are tested as well as `xml.sax` and
`xml.dom.minidom`. For each of the APIs one test creates its native
representation and one test transforms this into an UTF-8 encoded byte string,
as as most XML will ultimately be serialised in this form. The SAX tests
create byte strings in both test types.

**Running**

To run the [timeit](http://docs.python.org/2/library/timeit.html) tests
execute in a terminal from the project's root directory:

    python -m tests.performance.timeit_tests <string output> <repetitions> <data count> [<CSV output path>]

Use no arguments to get help.

To run a batch of tests with CPython 2.7, CPython 3.3 and PyPy, once to create
native structutres and once to create byte strings, writing the results to the
file `timeit.csv`, execute the Bash script `run_timeit_tests`.

Running [cProfile](http://docs.python.org/2/library/profile.html) tests:

    python tests/performance/profiling_tests.py


**Results**

These `timeit` tests show that the overhead of using ECoXiPy is not great and
the differences between using different APIs depend on the used Python
platform. If encoded strings are wanted as output, `ecoxipy.string_output` is
a viable alternative to using `xml.sax`.

Run the tests on your own or see my testing results in the repository under
[doc/perf_test_results/timeit.pdf](https://raw.github.com/IvIePhisto/ECoXiPy/master/doc/perf_test_results/timeit.pdf).

![Performance Testing Results Graph](https://raw.github.com/IvIePhisto/ECoXiPy/master/doc/perf_test_results/timeit.png)
