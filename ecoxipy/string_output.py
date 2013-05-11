# -*- coding: utf-8 -*-
u'''\

:mod:`ecoxipy.string_output` - XML as Strings
=============================================

:class:`StringOutput` creates strings of XML and aims at high performance by
using string concatenation.


.. _ecoxipy.string_output.examples:

Usage Example:

>>> xml_output = StringOutput()
>>> from ecoxipy import MarkupBuilder
>>> b = MarkupBuilder(xml_output)
>>> xml = b[:'section':False] (
...     b.section(
...         b.p('Hello World!'),
...         None,
...         b.p(u'äöüß'),
...         b.p(b & '<&>'),
...         b(
...             '<raw/>text', b.br,
...             (str(i) for i in range(3)), (str(i) for i in range(3, 6))
...         ),
...         b | '<This is a comment!>',
...         b['pi-target':'<PI content>'],
...         b['pi-without-content':],
...         attr='\\'"<&>'
...     )
... )
>>> xml.decode('utf-8') == u"""<?xml version="1.0"?>\\n<!DOCTYPE section><section attr="'&quot;&lt;&amp;&gt;"><p>Hello World!</p><p>äöüß</p><p>&lt;&amp;&gt;</p><raw/>text<br/>012345<!--<This is a comment!>--><?pi-target <PI content>?><?pi-without-content?></section>"""
True
'''

import xml.sax.saxutils

from tinkerpy import AttributeDict

from ecoxipy import Output, _python3, _unicode


_xml_strings_unicode = AttributeDict(
    lt=u'<',
    gt=u'>',
    equals=u'=',
    space=u' ',
    quot=u'"',
    element_empty_end=u'/>',
    element_close_start=u'</',
    comment_start=u'<!--',
    comment_end=u'-->',
    pi_start=u'<?',
    pi_end=u'?>',
    doctype_start=u'<!DOCTYPE ',
    doctype_public=u' PUBLIC "',
    doctype_system=u' SYSTEM "',
    doctype_id_divider=u'" "',
    xml_decl_start=u'<?xml version="1.0"',
    xml_decl_encoding=u' encoding="',
    xml_decl_end=u'?>\n',
)

_xml_strings_bytes = AttributeDict({
    key: value.encode() for key, value in _xml_strings_unicode.items()
})


class _XMLBytes(bytes): pass


if _python3:
    class _XMLUnicode(str): pass
else:
    class _XMLUnicode(unicode): pass


class StringOutput(Output):
    '''An :class:`ecoxipy.Output` implementation which creates XML as strings of the
    specified encoding.

    :param in_encoding: The name of the encoding to decode byte strings
        instances if neccessary.
    :param out_encoding: The name of the encoding to encode
        Unicode instances or :const:`None`.
    :param entities: A mapping of characters to text to replace them with
        when escaping.

    This class is aimed at high performance by working on string concatenation
    and omitting any sanity checks. This means it is the responsibility of
    using code to ensure well-formed XML is created.

    Element and attribute names, attribute values and text content data which
    are processed as follows:

        1.  Objects which are neither byte nor unicode strings are converted
            to Unicode.

        2.  If ``in_encoding`` and ``out_encoding`` differ, byte string
            instances are decoded to Unicode using ``in_encoding`` as the
            encoding.

        3.  Element and attribute names as well as attribute values are
            escaped using :func:`xml.sax.saxutils.escape`:

                * ``&``, ``<``, ``>`` are replaced by ``&amp;``, ``&lt;`` and
                  ``&gt;``

                * keys of ``entitites`` are replaced by the corresponding
                  value

            Attribute values are additionally quoted using
            :func:`xml.sax.saxutils.quoteattr`, which means ``'`` and ``"``
            are replaced by ``&apos;`` and ``&quot;``.

        4.  If ``out_encoding`` is not :const:`None` Unicode instances are
            encoded to byte strings.
    '''
    def __init__(self, in_encoding=u'utf-8', out_encoding=u'utf-8',
            entities=None):
        if entities is None:
            entities = {}
        self._entities = entities
        in_encoding = _unicode(in_encoding).lower()
        if out_encoding is not None:
            out_encoding = _unicode(out_encoding).lower()
        if in_encoding != out_encoding:
            self._decode = lambda value: (
                value.decode(in_encoding) if isinstance(value, bytes)
                else _unicode(value)
            )
        else:
            self._decode = lambda value: (
                value if isinstance(value, bytes) else _unicode(value))
        self._out_encoding = out_encoding
        if out_encoding is None:
            self._encode = lambda value: value
            self._xml_string = _XMLUnicode
            self._join = u''.join
            self._strings = _xml_strings_unicode
        else:
            self._encode = lambda value: (
                value.encode(out_encoding) if isinstance(value, _unicode)
                else value)
            self._xml_string = _XMLBytes
            self._join = b''.join
            self._strings = _xml_strings_bytes

    def _prepare_attr_value(self, value):
        return self._encode(
            xml.sax.saxutils.quoteattr(
                self._decode(value), self._entities))

    def _prepare_text(self, value):
        return self._encode(xml.sax.saxutils.escape(
            self._decode(value), self._entities))

    def _create_xml_string(self, generator):
        return self._xml_string(self._join([item for item in generator]))

    def element(self, name, children, attributes):
        '''\
        Creates an element string.

        :returns: The element created.
        '''
        def element_creator():
            element_name = self._prepare_text(name)
            yield self._strings.lt
            yield element_name
            for attr_name, attr_value in attributes.items():
                yield self._strings.space
                yield self._prepare_text(attr_name)
                yield self._strings.equals
                yield self._prepare_attr_value(attr_value)
            if len(children) == 0:
                yield self._strings.element_empty_end
            else:
                yield self._strings.gt
                for child in children:
                    if isinstance(child, self._xml_string):
                        yield child
                    else:
                        yield self._prepare_text(child)
                yield self._strings.element_close_start
                yield element_name
                yield self._strings.gt
        return self._create_xml_string(element_creator())

    def embed(self, content):
        '''\
        Treats the content items as XML fragments.

        :returns: A string.
        '''
        if len(content) == 1:
            content = content[0]
            return (
                content if isinstance(content, self._xml_string)
                else self._xml_string(self._encode(self._decode(content)))
            )
        else:
            return self._create_xml_string(
                    item if isinstance(item, self._xml_string)
                    else self._encode(self._decode(item))
                for item in content
            )

    def text(self, content):
        '''\
        Creates text string.

        :returns: The created text.
        '''
        return self._xml_string(self._prepare_text(content))

    def comment(self, content):
        '''\
        Creates a comment string.

        :returns: The created comment.
        '''
        def comment_creator():
            yield self._strings.comment_start
            yield self._encode(self._decode(content))
            yield self._strings.comment_end
        return self._create_xml_string(comment_creator())


    def processing_instruction(self, target, content):
        '''\
        Creates a processing instruction string.

        :returns: The created processing instruction.
        '''
        def pi_creator():
            yield self._strings.pi_start
            yield self._encode(self._decode(target))
            if content is not None:
                yield self._strings.space
                yield self._encode(self._decode(content))
            yield self._strings.pi_end
        return self._create_xml_string(pi_creator())

    def document(self, doctype_name, doctype_publicid, doctype_systemid,
            children, omit_xml_declaration):
        '''\
        Creates a XML document.

        :returns: The created document.
        '''
        def document_creator():
            if not omit_xml_declaration:
                if self._out_encoding is None:
                    raise ValueError(
                        'Neither output encoding given nor XML declaration omitted.')
                yield self._strings.xml_decl_start
                if self._out_encoding != u'utf-8':
                    yield self._strings.xml_decl_encoding
                    yield self._encode(self._decode(self._out_encoding))
                    yield self._strings.quot
                yield self._strings.xml_decl_end
            if doctype_name is not None:
                yield self._strings.doctype_start
                yield self._encode(self._decode(doctype_name))
                if doctype_publicid is None:
                    if doctype_systemid is not None:
                        yield self._strings.doctype_system
                        yield self._encode(self._decode(doctype_system))
                        yield self._strings.quot
                else:
                    yield self._strings.doctype_public
                    yield self._encode(self._decode(doctype_public))
                    if doctype_systemid is not None:
                        yield self._strings.doctype_id_divider
                        yield self._encode(self._decode(doctype_system))
                    yield self._strings.quot
                yield self._strings.gt
            for child in children:
                if isinstance(child, self._xml_string):
                    yield child
                else:
                    yield self._prepare_text(child)
        return self._create_xml_string(document_creator())


del Output, AttributeDict
