# -*- coding: utf-8 -*-

ur'''\
:class:`ecoxipy.string_output.StringOutput` creates strings of encoded
XML and is aimed at high performance by using string concatenation:

>>> xml_output = StringOutput(out_encoding=None)
>>> from ecoxipy import MarkupBuilder
>>> b = MarkupBuilder(xml_output)
>>> xml = b.section(b.p('Hello World!'), None, b.p(u'äöüß'), b.p('<&>'), b('<raw/>text', b.br, (str(i) for i in range(3)), (str(i) for i in range(3, 6))), attr='\'"<&>')
>>> xml == u"""<section attr="'&quot;&lt;&amp;&gt;"><p>Hello World!</p><p>äöüß</p><p>&lt;&amp;&gt;</p><raw/>text<br/>012345</section>"""
True
'''


from xml.sax.saxutils import escape, quoteattr

from . import Output


class StringOutput(Output):
    '''A :class:`Output` implementation which creates XML as strings of the
    specified encoding.

    :param in_encoding: The name of the encoding to decode :class:`str`
        instances if neccessary.
    :param out_encoding: The name of the encoding to encode
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
        element_name = self._escape(self._encode(self._decode(name)))
        attributes_string = self._join([
            self._format_attribute.format(
                self._escape(self._encode(self._decode(attribute_name))),
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
                    else self._escape(self._encode(self._decode(child)))
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


def xml_string_namespace(builder_name, vocabulary):
    ur'''\
    Uses :func:`ecoxipy.markup_builder_namespace` to decorate the target
    function with the given ``vocabulary``.

    :param builder_name: The name the :class:`MarkupBuilder` instance is
        available under.
    :param vocabulary: An iterable of element names.
    :returns: The decorated function with it's namespace extented with the
        element creators defined by the vocabulary.


    Example:

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
    ...         attr='\'"<&>'
    ...     )
    ...
    >>> view('Hello World!') == u"""<section attr="'&quot;&lt;&amp;&gt;"><p>Hello World!</p><p>äöüß</p><p>&lt;&amp;&gt;</p><raw/>text<br/>012345</section>""".encode('utf-8')
    True
    '''
    from tinkerpy import flatten
    from . import markup_builder_namespace
    return markup_builder_namespace(StringOutput, builder_name,
        *flatten(vocabulary))

