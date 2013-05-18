ECoXiPy - Easy Creation of XML in Python
========================================

This Python 2 and 3 project (tested with 2.7 and 3.3) allows for easy creation
of `XML <http://www.w3.org/XML/>`_. The hierarchical structure of XML is easy
to spot and the code to create XML is much shorter than using SAX, DOM or
similar APIs.

Modules
--------

.. toctree::

    base
    string_output
    dom_output
    pyxom
    pyxom_output
    decorators
    parsing


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

Create :mod:`ecoxipy.pyxom` structures

    :ref:`ecoxipy.pyxom_output <ecoxipy.pyxom_output.examples>`



See this example of how to create a simple HTML5 document template function::

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


It could be used like this:

>>> create_testdoc('Test', 'A Simple Test Document', 'Hello World & Universe!', 'How are you?')
'<!DOCTYPE html><html data-info="Created by Ecoxipy" xmlns="http://www.w3.org/1999/xhtml/"><head><title>Test</title></head><body><article><h1>Test</h1><h2>A Simple Test Document</h2><p>Hello World &amp; Universe!</p><p>How are you?</p><hr/>&lt;THE END&gt;<footer>Copyright 2013</footer><!--This is a comment.--><?pi-target PI content.?></article></body></html>'


Pretty-printing the result yields the following HTML::

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


.. [#f1] "*Too long; didn't read*"
