# -*- coding: utf-8 -*-

from . import Output


class StringOutput(Output):
    '''A :class:`Output` implementation which creates XML as strings of the
    specified encoding.

    :param in_encoding: The name of the encoding to use decode :class:`str`
        instances if neccessary.
    :param out_encoding: The name of the encoding to use encode
        :class:`unicode` instances or :const:`None`.
    :param entities: A mapping of characters to text to replace them with
        when escaping.

    This class is aimed at high performance by working on string concatenation
    and omitting any sanity checks. This means it is the responsibility of
    using code to ensure well-formed XML is created.

    Element and attribute names, attribute values and text content data which
    are processed as follows:

        * Instances which are neither :class:`str` or :class:`unicode`
          instances converted using :func:`unicode`.

        * If ``in_encoding`` and ``out_encoding`` differ, :class:`str`
          instances are decoded to :class:`unicode` using ``in_encoding`` as
          the encoding.

        * :class:`unicode` instances are left untouched.

    ``encoding`` is :const:`None`
        :class:`unicode` instances are not processed. Non-:class:`str`
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

        * :class:`str` instances are left untouched. There are none if
          ``out_encoding`` differs from ``in_encoding``.

        * :class:`unicode` instances are left untouched if ``out_encoding`` is
          :const:`None`, otherwise they are encoded using ``out_encoding`` as
          the encoding.
    '''
    def __init__(self, in_encoding='utf-8', out_encoding='utf-8',
            entities=None):
        self._in_encoding = in_encoding
        self._out_encoding = out_encoding
        self._different_encodings = in_encoding == out_encoding
        if out_encoding is None:
            self._join = u''.join
            self._format_attribute = u' {}={}'
            self._format_element = u'<{0}{1}>{2}</{0}>'
            self._format_element_empty = u'<{0}{1}/>'
            self._xml_string = _XMLUnicode
        else:
            self._join = ''.join
            self._format_attribute = ' {}={}'
            self._format_element = '<{0}{1}>{2}</{0}>'
            self._format_element_empty = '<{0}{1}/>'
            self._xml_string = _XMLStr
        if entities is None:
            entities = {}
        self._entities = entities

    def _decode(self, value):
        if isinstance(value, str):
            if self._different_encodings and self._in_encoding is not None:
                return value.decode(self._in_encoding)
            return value
        elif isinstance(value, unicode):
            return value
        else:
            return unicode(value)

    def _encode(self, value):
        if self._out_encoding is not None and isinstance(value, unicode):
            return value.encode(self._out_encoding)
        return value

    def _escape(self, value):
        return escape(value, self._entities)

    def _quoteattr(self, value):
        return quoteattr(value, self._entities)

    def element(self, name, children, attributes):
        '''Returns a XML element string with the encoding given on
        initialization.

        :param name: The name of the element to create.
        :type name: :class:`str` of :class:`unicode`
        :param children: The iterable of children.
        :param attributes: The mapping of arguments.
        :returns: The XML string created.
        :rtype: class:`str`
        '''
        element_name = self._escape(self._decode(name))
        attributes_string = self._join([
            self._format_attribute.format(
                self._escape(self._decode(attribute_name)),
                self._quoteattr(
                        self._decode(attributes[attribute_name])
                )
            )
            for attribute_name in attributes
        ])
        # TODO finish decoding, encoding
        if len(children) == 0:
            element_string = self._format_element_empty.format(
                element_name, attributes_string)
        else:
            children_string = self._join([
                child if isinstance(child, self._xml_string)
                    else self._escape(child)
                for child in children
            ])
            element_string = self._format_element.format(
                element_name, attributes_string, children_string)
        return self._xml_string(element_string)

    def embed(self, *content):
        '''Encodes the elements of ``content`` if they are not :class:`str`
        instances.

        :param content: The content to encode.
        :type content: :class:`str` or :class:`unicode`
        :returns: a :class:`list` of :class:`str` instances or a single
            instance
        '''
        def handle_content(value):
            if isinstance(value, self._xml_string):
                return value
            return self._encode(self._decode(value))
        if len(content) == 1:
            return handle_content(content[0])
        return self._xml_string(self._join([
            handle_content(content_element) for content_element in content
        ]))

class _XMLStr(str): pass

class _XMLUnicode(unicode): pass

