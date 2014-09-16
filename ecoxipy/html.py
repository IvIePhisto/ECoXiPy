# -*- coding: utf-8 -*-
u'''\

:mod:`ecoxipy.html5` - HTML5 Functionality
==========================================

This module contains HTML-related functionality.


.. _ecoxipy.decorators.examples:

Examples
--------

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


API
---

.. py:function:: html5(func)

    This is a decorator created by a :func:`tinkerpy.namespace`
    using :class:`ecoxipy.MarkupBuilder` with
    :class:`ecoxipy.string_output.StringOutput`. The function/method it is
    applied to is able to create `HTML5 <http://www.w3.org/TR/html5/>`_
    content as UTF8-encoded :func:`str` objects. The
    :class:`ecoxipy.MarkupBuilder` instance is available as ``_b``.

.. autofunction:: html5_template

.. autofunction:: html5_cats

.. py:data:: HTML5_ELEMENTS

    This :class:`tinkerpy.ImmutableDict` instance contains
    :class:`frozenset` instances representing the categories of
    elements defined by `HTML5 - The elements of HTML
    <http://www.w3.org/TR/html5/semantics.html#semantics>`_. Each set contains
    for each element contained in the respective category a :func:`str` equal
    to the element's name. The category names are converted to snake case,
    thus they are named: ``root_element``, ``document_metadata``,
    ``scripting``, ``sections``, ``grouping_content``,
    ``text_level_semantics``, ``edits``, ``embedded_content``,
    ``tabular_data``, ``forms`` and ``interactive_elements``.

.. py:data:: HTML5_ELEMENT_NAMES

    An :func:`frozenset` of all HTML5 element names as defined in
    :data:`HTML5_ELEMENTS`.

'''

from xml.dom import XHTML_NAMESPACE

import tinkerpy

from ecoxipy.decorators import xml_string_namespace


def HTML5_ELEMENTS():
    return tinkerpy.ImmutableDict(dict(
        root_element = frozenset({'html'}),
        document_metadata = frozenset({'head', 'title', 'base', 'link', 'meta',
            'style'}),
        scripting = frozenset({'script', 'noscript'}),
        sections = frozenset({'body', 'article', 'section', 'nav', 'aside',
            'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'hgroup', 'header', 'footer',
            'address'
        }),
        grouping_content = frozenset({'p', 'hr', 'pre', 'blockquote', 'ol',
            'ul', 'li', 'dl', 'dt', 'dd', 'figure', 'figcaption', 'div'
        }),
        text_level_semantics = frozenset({'a', 'em', 'strong', 'small', 's',
            'cite', 'q', 'dfn', 'abbr', 'data', 'time', 'code', 'var', 'samp',
            'kbd', 'sub', 'sup', 'i', 'b', 'u', 'mark', 'ruby', 'rt', 'rp',
            'bdi', 'bdo', 'span', 'br', 'wbr'
        }),
        edits = frozenset({'ins', 'del'}),
        embedded_content = frozenset({'img', 'iframe', 'embded', 'object',
            'param', 'video', 'audio', 'source', 'track', 'canvas', 'map',
            'area'
        }),
        tabular_data = frozenset({'table', 'caption', 'colgroup', 'col',
            'tbody', 'thead', 'tfoot', 'tr', 'td', 'th'
        }),
        forms = frozenset({'form', 'fieldset', 'legend', 'label', 'input',
            'button', 'select', 'datalist', 'optgroup', 'option', 'textarea',
            'keygen', 'output', 'progress', 'meter'
        }),
        interactive_elements = frozenset({'details', 'summary', 'command',
            'menu', 'dialog'})
    ))


HTML5_ELEMENTS = HTML5_ELEMENTS()
HTML5_ELEMENT_NAMES = frozenset(tinkerpy.flatten(HTML5_ELEMENTS))


html5 = xml_string_namespace('_b', HTML5_ELEMENT_NAMES)


def html5_cats(*categories):
    '''\
    Returns a function decorator like :func:`html5`, but only with those
    element names available defined in the HTML5 categories (as defined in
    :attr:`HTML5_ELEMENTS`) given as ``categories``. The
    :class:`ecoxipy.MarkupBuilder` instance is available as ``_b`` in
    decorated functions.

    :param categories: The names of the HTML5 categories to use to define
        the XML namespace.
    :returns: A function decorator making element creators for the elements
        from the given categories available.
    :raises KeyError: If a category is not found in :attr:`HTML5_ELEMENTS`.

    Example:

    >>> @html5_cats('sections', 'grouping_content')
    ... def page_part(_title, *texts):
    ...     return section(
    ...          h1(_title),
    ...          (p(text) for text in texts)
    ...      )

    >>> print(page_part('Test', 'Foo.', 'Bar.', 'Foo Bar!'))
    <section><h1>Test</h1><p>Foo.</p><p>Bar.</p><p>Foo Bar!</p></section>

    '''
    element_names = set()
    for category in categories:
        element_names.update(HTML5_ELEMENTS[category])
    return xml_string_namespace('_b', element_names)


def html5_template(builder, title, body_contents, keywords=None,
        description=None, lang='en', head_contents=None):
    '''\
    A HTML5 template (with XML syntax, omitting the XML declaration), which uses
    the given markup builder. The first head element is a ``meta`` setting the
    HTTP header ``Content-Type`` to ``text/html;charset=UTF-8``.

    :param builder: The builder to use.
    :type builder: :class:`ecoxipy.MarkupBuilder`
    :param title: The document head's title child, creates a text node.
    :param body_contents: The document body's children. This will be parsed as
        XML, if not already in the output representation.
    :param keywords: The content of the ``keywords`` meta element, if
        :const:`None` no such element will be created.
    :param description: The content of the ``description`` meta element, if
        :const:`None` no such element will be created.
    :param lang: The value of the document's html element's ``lang``
        attribute, if this is :const:`None` no such attribute will be created.
    :param head_contents: Additional children for the document head. This will
        be parsed as XML, if not already in the output representation.
    :returns: A HTML5 XML document without XML declaration in the builder's
        output representation.
    '''
    return builder[:'html':True](
        builder.html(
            builder.head(
                builder.meta({'http-equiv':'Content-Type',
                    'content':'text/html;charset=UTF-8'}),
                builder.title(builder & title),
                None if keywords is None else
                    builder.meta(name='keywords', content=keywords),
                None if description is None else
                    builder.meta(name='description', content=description),
                builder(head_contents)
            ),
            builder.body(
                builder(body_contents)
            ),
            None if lang is None else {'lang': lang},
            xmlns=XHTML_NAMESPACE
        )
    )

