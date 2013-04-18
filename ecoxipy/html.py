ur'''\

This module provides `HTML <http://www.w3.org/html/>`_ related functionality.

.. py:data:: HTML5_ELEMENTS

    This :class:`tinkerpy.ImmutableDict` instance contains
    :class:`frozenset` instances representing the categories of
    elements defined by `HTML5 - The elements of HTML
    <http://www.w3.org/TR/html5/semantics.html#semantics>`_. Each set contains
    for each element contained in the respective category a :class:`str` equal
    to the element's name.

.. py:function:: html()

    This is a decorator created by a :func:`tinkerpy.namespace`
    using :class:`ecoxipy.MarkupBuilder` with
    :class:`ecoxipy.string_output.StringOutput`. The function/method it is
    applied to is able to create `HTML5 <http://www.w3.org/TR/html5/>`_ content as
    UTF8-encoded :class:`str` objects.  The :class:`MarkupBuilder` instance is
    available as ``_b``.

    Example:

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
    >>> print page('Test', 'Hello World & Universe!')
    <html><head><title>Test</title></head><body><h1>Test</h1><p>Hello World &amp; Universe!</p><footer>Copyright</footer></body></html>
'''
import tinkerpy


def HTML5_ELEMENTS():
    from tinkerpy import ImmutableDict
    return ImmutableDict(dict(
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


def html5():
    from string_output import xml_string_namespace
    return xml_string_namespace('_b', HTML5_ELEMENTS)

html5 = html5()
