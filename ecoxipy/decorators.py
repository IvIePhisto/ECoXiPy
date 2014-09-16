# -*- coding: utf-8 -*-
u'''\

:mod:`ecoxipy.decorators` - Decorators for Shorter XML-Creation Code
====================================================================

The decorators in the module :mod:`ecoxipy.decorators` make the code to create
XML using :class:`ecoxipy.MarkupBuilder` shorter.

**Important:** The decorators use :func:`tinkerpy.namespace` to modify the
globals of a function, so on certain Python runtimes (e.g. CPython 2.7) updates
to the global dictionary after application of the decorator are not available in
the function, on other runtimes (e.g. CPython 3.3 or PyPy) this restriction does
not apply.


.. _ecoxipy.decorators.examples:

Examples
--------

:func:`markup_builder_namespace` creates a :func:`tinkerpy.namespace`
decorator to create XML using a newly created
:class:`ecoxipy.MarkupBuilder` instance. It takes an
:class:`ecoxipy.Output` implementation, the name under which the builder is
available and a list of allowed element names:

>>> from ecoxipy.string_output import StringOutput
>>> builds_html = markup_builder_namespace(StringOutput, '_b', 'section', 'p', 'br')
>>> @builds_html
... def view(value):
...     return section(
...         p(value),
...         None,
...         p(u'äöüß'),
...         p('<&>'),
...         _b('<raw/>text'),
...         _b(br, (str(i) for i in range(3))),
...         (str(i) for i in range(3, 6)),
...         attr='\\'"<&>'
...     )
...
>>> view('Hello World!') == u"""<section attr="'&quot;&lt;&amp;&gt;"><p>Hello World!</p><p>äöüß</p><p>&lt;&amp;&gt;</p><raw/>text<br/>012345</section>"""
True


:func:`xml_string_namespace` is a shorthand of :func:`markup_builder_namespace`
using :class:`ecoxipy.string_output.StringOutput` as the
:class:`ecoxipy.Output` implementation:

>>> builds_html = xml_string_namespace('_b', {'section', 'p', 'br'})
>>> @builds_html
... def view(value):
...     return section(
...         p(value),
...         None,
...         p(u'äöüß'),
...         p('<&>'),
...         _b('<raw/>text', br, (str(i) for i in range(3))),
...         (str(i) for i in range(3, 6)),
...         attr='\\'"<&>'
...     )
...
>>> view('Hello World!') == u"""<section attr="'&quot;&lt;&amp;&gt;"><p>Hello World!</p><p>äöüß</p><p>&lt;&amp;&gt;</p><raw/>text<br/>012345</section>"""
True


Decorator Creation
------------------

.. autofunction:: markup_builder_namespace

.. autofunction:: xml_string_namespace
'''
import tinkerpy

from ecoxipy import MarkupBuilder
from ecoxipy.string_output import StringOutput


def markup_builder_namespace(output, builder_name, *element_names, **kargs):
    '''\
    A function creating a :func:`tinkerpy.namespace` decorator. It has all in
    ``element_names`` defined names bound to the appropriate `virtual` methods
    of a new :class:`ecoxipy.MarkupBuilder` instance, which uses a new
    instance of the given ``output`` class.

    :param output: The output class to use.
    :type output: :class:`ecoxipy.Output`
    :param builder_name: The name the :class:`MarkupBuilder` instance is
        available under.
    :param element_names: The names to bind to the appropriate `virtual`
        builder methods.
    :param kargs: Arguments passed to the ``output`` constructor.
    :returns: The created decorater function. In its attribute ``builder`` the
        builder created is accessible.
    '''
    builder = MarkupBuilder(output(**kargs))
    namespace = tinkerpy.namespace(builder,
        *element_names,
        **{builder_name: builder}
    )
    namespace.builder = builder
    return namespace


xml_string_namespace = lambda builder_name, vocabulary: markup_builder_namespace(
        StringOutput, builder_name, *vocabulary)
'''\
Uses :func:`markup_builder_namespace` with the given ``vocabulary`` and
:class:`ecoxipy.string_output.StringOutput` to create a decorator, that
allows for creation of UTF8-encoded XML strings.

:param builder_name: The name the :class:`ecoxipy.MarkupBuilder` instance is
    available under.
:param vocabulary: An iterable of element names.
:returns: The decorated function with it's namespace extented with the
    element creators defined by the ``vocabulary``.
'''

