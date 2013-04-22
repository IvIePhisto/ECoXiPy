ECoXiPy - Easy Creation of XML in Python
========================================

This Python project allows for easy creation of `XML
<http://www.w3.org/XML/>`_. The hierarchical structure of XML is easy to spot
and the code to create XML is much shorter than using SAX, DOM or similar
APIs.


See this example of how to create a simple HTML5 document template function::

    from ecoxipy.decorators import html5

    @html5
    def create_testdoc(_title, _content):
        return _b(
            '<!DOCTYPE html>',
            html(
                head(
                    title(_title)
                ),
                body(
                    h1(_title),
                    p(_content)
                ),
                xmlns='http://www.w3.org/1999/xhtml/'
            )
        )


This can be used like this:

>>> create_testdoc('A Test', 'Hello World!')
'<!DOCTYPE html><html xmlns="http://www.w3.org/1999/xhtml/"><head><title>A Test</title></head><body><h1>A Test</h1><p>Hello World!</p></body></html>'


Chapters
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