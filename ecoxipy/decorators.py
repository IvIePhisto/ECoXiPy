# -*- coding: utf-8 -*-
u'''\

:mod:`ecoxipy.decorators` - Decorators for Shorter XML-Creation Code
====================================================================

The decorators in the module :mod:`ecoxipy.decorators` make the code to create
XML using :class:`ecoxipy.MarkupBuilder` shorter.


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


To create `HTML5 <http://www.w3.org/TR/html5/>`_ XML strings use the
:func:`html5` decorator:

>>> @html5
... def page(page_title, page_content):
...     return html(
...         head(
...             title(page_title)
...         ),
...         body(
...             h1(page_title),
...             p(page_content),
...             _b('<footer>Copyright</footer>')
...         ),
...     )
>>> page('Test', 'Hello World & Universe!') == u'<html><head><title>Test</title></head><body><h1>Test</h1><p>Hello World &amp; Universe!</p><footer>Copyright</footer></body></html>'
True


Decorator Creation
------------------

.. autofunction:: markup_builder_namespace

.. autofunction:: xml_string_namespace


HTML5
-----

.. py:function:: html5()

    This is a decorator created by a :func:`tinkerpy.namespace`
    using :class:`ecoxipy.MarkupBuilder` with
    :class:`ecoxipy.string_output.StringOutput`. The function/method it is
    applied to is able to create `HTML5 <http://www.w3.org/TR/html5/>`_
    content as UTF8-encoded :func:`str` objects.  The
    :class:`ecoxipy.MarkupBuilder` instance is available as ``_b``.


.. py:data:: HTML5_ELEMENTS

    This :class:`tinkerpy.ImmutableDict` instance contains
    :class:`frozenset` instances representing the categories of
    elements defined by `HTML5 - The elements of HTML
    <http://www.w3.org/TR/html5/semantics.html#semantics>`_. Each set contains
    for each element contained in the respective category a :func:`str` equal
    to the element's name.

.. py:data:: HTML5_ELEMENT_NAMES

    An :func:`frozenset` of all HTML5 element names as defined in
    :data:`HTML5_ELEMENTS`.

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
    :type output: :class:`Output`
    :param builder_name: The name the :class:`MarkupBuilder` instance is
        available under.
    :param element_names: The names to bind to the appropriate `virtual`
        builder methods.
    :param kargs: Arguments passed to the ``output`` constructor.
    :returns: The decorated function with it's namespace extented by the
        element creators, as defined by ``element_names``.
    '''
    builder = MarkupBuilder(output(**kargs))
    return tinkerpy.namespace(builder,
        *element_names,
        **{builder_name: builder}
    )


xml_string_namespace = lambda builder_name, vocabulary: markup_builder_namespace(
        StringOutput, builder_name, *vocabulary)
'''\
Uses :func:`markup_builder_namespace` to decorate the target
function with the given ``vocabulary``.

:param builder_name: The name the :class:`ecoxipy.MarkupBuilder` instance is
    available under.
:param vocabulary: An iterable of element names.
:returns: The decorated function with it's namespace extented with the
    element creators defined by the ``vocabulary``.
'''


def HTML5_ELEMENTS():
    return tinkerpy.ImmutableDict(dict(
        root_element = frozenset({'html'}),
        document_metadata = frozenset({'head', 'title', 'base', 'link', 'meta', 'style'}),
        scripting = frozenset({'script', 'noscript'}),
        sections = frozenset({'body', 'article', 'section', 'nav', 'aside', 'h1', 'h2',
            'h3', 'h4', 'h5', 'h6', 'hgroup', 'header', 'footer', 'address'
        }),
        grouping_content = frozenset({'p', 'hr', 'pre', 'blockquote', 'ol', 'ul', 'li',
            'dl', 'dt', 'dd', 'figure', 'figcaption', 'div'
        }),
        text_level_semantics = frozenset({'a', 'em', 'strong', 'small', 's', 'cite', 'q',
            'dfn', 'abbr', 'data', 'time', 'code', 'var', 'samp', 'kbd', 'sub',
            'sup', 'i', 'b', 'u', 'mark', 'ruby', 'rt', 'rp', 'bdi', 'bdo',
            'span', 'br', 'wbr'
        }),
        edits = frozenset({'ins', 'del'}),
        embedded_content = frozenset({'img', 'iframe', 'embded', 'object', 'param', 'video',
            'audio', 'source', 'track', 'canvas', 'map', 'area'
        }),
        tabular_data = frozenset({'table', 'caption', 'colgroup', 'col', 'tbody', 'thead',
            'tfoot', 'tr', 'td', 'th'
        }),
        forms = frozenset({'form', 'fieldset', 'legend', 'label', 'input', 'button',
            'select', 'datalist', 'optgroup', 'option', 'textarea', 'keygen',
            'output', 'progress', 'meter'
        }),
        interactive_elements = frozenset({'details', 'summary', 'command', 'menu', 'dialog'})
    ))


HTML5_ELEMENTS = HTML5_ELEMENTS()
HTML5_ELEMENT_NAMES = frozenset(tinkerpy.flatten(HTML5_ELEMENTS))

def html5():
    return xml_string_namespace('_b', HTML5_ELEMENT_NAMES)

html5 = html5()
