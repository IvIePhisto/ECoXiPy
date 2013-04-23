ECoXiPy - Easy Creation of XML in Python
========================================

This Python project allows for easy creation of `XML
<http://www.w3.org/XML/>`_. The hierarchical structure of XML is easy to spot
and the code to create XML is much shorter than using SAX, DOM or similar
APIs.


See this example of how to create a simple HTML5 document template function::

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


It could be used like this:

>>> create_testdoc('Test', 'A Simple Test Document', 'Hello World & Universe!', 'How are you?')
'<!DOCTYPE html><html xmlns="http://www.w3.org/1999/xhtml/"><head><title>Test</title></head><body><h1>Test</h1><h2>A Simple Test Document</h2><p>Hello World &amp; Universe!</p><p>How are you?</p><hr/><footer>Copyright 2013</footer></body></html>'


Pretty-printing the result yields the following HTML::

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


Contents
--------

.. toctree::

    base
    decorators
    string_output
    dom_output
    element_output


TL;DR [#f1]_
------------

If you want to jump right in, have a look at the examples...


The most convenient usage - if you can live with defining allowed element
names beforehand, want to define a vocabulary anyway or just want to create
HTML5:

    :ref:`ecoxipy.decorators <ecoxipy.decorators.examples>`

XML as Strings

    :ref:`ecoxipy.string_output <ecoxipy.string_output.examples>`

DOM Creation

    :ref:`ecoxipy.dom_output <ecoxipy.dom_output.examples>`

Create low-footprint XML structures

    :ref:`ecoxipy.element_output <ecoxipy.element_output.examples>`


.. [#f1] "*Too long; didn't read*"