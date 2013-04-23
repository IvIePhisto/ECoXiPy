# -*- coding: utf-8 -*-
ur'''\

:mod:`ecoxipy.string_output` - XML as Strings
=============================================

:class:`StringOutput` creates strings of XML and aims at high performance by
using string concatenation.


.. _ecoxipy.string_output.examples:

Usage Example:

>>> xml_output = StringOutput(out_encoding=None)
>>> from ecoxipy import MarkupBuilder
>>> b = MarkupBuilder(xml_output)
>>> xml = b.section(b.p('Hello World!'), None, b.p(u'äöüß'), b.p(b & '<&>'), b('<raw/>text', b.br, (str(i) for i in range(3)), (str(i) for i in range(3, 6))), attr='\'"<&>')
>>> xml == u"""<section attr="'&quot;&lt;&amp;&gt;"><p>Hello World!</p><p>äöüß</p><p>&lt;&amp;&gt;</p><raw/>text<br/>012345</section>"""
True
'''


from xml.sax.saxutils import escape, quoteattr

from . import Output


class StringOutput(Output):
    '''An :class:`ecoxipy.Output` implementation which creates XML as strings of the
    specified encoding.

    :param in_encoding: The name of the encoding to decode :func:`str`
        instances if neccessary.
    :param out_encoding: The name of the encoding to encode
        :func:`unicode` instances or :const:`None`.
    :param entities: A mapping of characters to text to replace them with
        when escaping.

    This class is aimed at high performance by working on string concatenation
    and omitting any sanity checks. This means it is the responsibility of
    using code to ensure well-formed XML is created.

    Element and attribute names, attribute values and text content data which
    are processed as follows:

        * Instances which are neither :func:`str` or :func:`unicode`
          instances converted using :func:`unicode`.

        * If ``in_encoding`` and ``out_encoding`` differ, :func:`str`
          instances are decoded to :func:`unicode` using ``in_encoding`` as
          the encoding.

        * :func:`unicode` instances are left untouched.

    ``encoding`` is :const:`None`
        :func:`unicode` instances are not processed. Non-:func:`str`
        instances are

    Element and attribute names as well as attribute values are escaped using
    :func:`xml.sax.saxutils.escape`:

        * ``&``, ``<``, ``>`` are replaced by ``&amp;``, ``&lt;`` and ``&gt;``

        * keys of ``entitites`` are replaced by the corresponding value

    Attribute values are additionally quoted using
    :func:`xml.sax.saxutils.quoteattr`, which means ``'`` and ``"`` are
    replaced by ``&apos;`` and ``&quot;``.

    The possibly converted, decoded, escaped and/or quoted element and
    attribute names, attribute values and text content data is then
    processed as follows depending on the type:

        * :func:`str` instances are left untouched. There are none if
          ``out_encoding`` differs from ``in_encoding``.

        * :func:`unicode` instances are left untouched if ``out_encoding`` is
          :const:`None`, otherwise they are encoded using ``out_encoding`` as
          the encoding.
    '''
    def __init__(self, in_encoding='utf-8', out_encoding='utf-8',
            entities=None):
        if in_encoding != out_encoding and in_encoding is not None:
            self._decode = lambda value: (
                value.decode(in_encoding)
                if isinstance(value, str) else unicode(value)
            )
        else:
            self._decode = lambda value: (
                value if isinstance(value, str) else unicode(value)
            )
        if out_encoding is None:
            self._encode = lambda value: value
        else:
            self._encode = lambda value: (
                value.encode(out_encoding)
                if isinstance(value, unicode) else value
            )
        if out_encoding is None:
            self._xml_string = _XMLUnicode
            self._join = u''.join
            self._format_element = u'<{0}{1}>{2}</{0}>'
            self._format_element_empty = u'<{0}{1}/>'
            self._format_attribute = u' {}={}'
        else:
            self._xml_string = _XMLStr
            self._join = ''.join
            self._format_element = '<{0}{1}>{2}</{0}>'
            self._format_element_empty = '<{0}{1}/>'
            self._format_attribute = ' {}={}'
        if entities is None:
            entities = {}
        self._entities = entities

    def _escape(self, value):
        return escape(value, self._entities)

    def _quoteattr(self, value):
        return quoteattr(value, self._entities)

    def _prepare(self, value):
        return self._escape(self._encode(self._decode(value)))

    def element(self, name, children, attributes):
        '''Returns a XML element string with the encoding given on
        initialization.

        :param name: The name of the element to create.
        :param children: The iterable of children.
        :param attributes: The mapping of arguments.
        :returns: The XML string created.
        :rtype: :func:`str` or :func:`unicode`
        '''
        element_name = self._prepare(name)
        attributes_string = self._join([
            self._format_attribute.format(
                self._prepare(attribute_name),
                self._quoteattr(self._encode(self._decode(
                    attributes[attribute_name])))
            )
            for attribute_name in attributes
        ])
        if len(children) == 0:
            element_string = self._format_element_empty.format(
                element_name, attributes_string)
        else:
            children_string = self._join([
                child if isinstance(child, self._xml_string)
                    else self._prepare(child)
                for child in children
            ])
            element_string = self._format_element.format(
                element_name, attributes_string, children_string)
        return self._xml_string(element_string)

    def embed(self, content):
        '''Encodes the elements of ``content`` if they are not :func:`str`
        or :func:`unicode` instances.

        :param content: The content to encode.
        :returns: a :func:`list` of :func:`str` instances or a single
            instance
        '''
        def handle_content(value):
            if isinstance(value, self._xml_string):
                return value
            return self._encode(self._decode(value))
        if len(content) == 1:
            return self._xml_string(handle_content(content[0]))
        return self._xml_string(self._join([
            handle_content(content_item) for content_item in content
        ]))

    def text(self, content):
        '''\
        Creates :func:`str` or :func:`unicode` instances from the items of
        ``content``, depending on the instance's ``out_encoding``.

        :param content: The list of texts.
        :returns: A list of :func:`str` or :func:`unicode` instances.
        '''
        imported = []
        for content_item in content:
            content_item = self._prepare(content_item)
            imported.append(self._xml_string(content_item))
        if len(imported) == 1:
            return imported[0]
        return imported


class _XMLStr(str): pass

class _XMLUnicode(unicode): pass

