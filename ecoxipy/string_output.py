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
>>> xml = b[:'section'] (
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
>>> xml == u"""<?xml version="1.0"?>\\n<!DOCTYPE section><section attr="'&quot;&lt;&amp;&gt;"><p>Hello World!</p><p>äöüß</p><p>&lt;&amp;&gt;</p><raw/>text<br/>012345<!--<This is a comment!>--><?pi-target <PI content>?><?pi-without-content?></section>"""
True
'''

import xml.sax.saxutils
import string

from ecoxipy import Output, _python3, _unicode


class StringOutput(Output):
    '''\
    An :class:`ecoxipy.Output` implementation which creates XML as strings.

    :param entities: A mapping of characters to text to replace them with
        when escaping.

    This class is aimed at high performance by working on string concatenation
    and omitting any sanity checks. This means it is the responsibility of
    using code to ensure well-formed XML is created, especially in processing
    instructions, comments and the document type URIs.
    '''
    def __init__(self, entities=None):
        if entities is None:
            entities = {}
        self._entities = entities
        self._join = u''.join
        self._format_element = u'<{0}{1}>{2}</{0}>'.format
        self._format_element_empty = u'<{}{}/>'.format
        self._format_attribute = u' {}={}'.format
        self._format_pi = u'<?{}{}?>'.format
        self._format_comment = u'<!--{}-->'.format
        self._format_document = u'{}{}{}'.format
        self._format_xml_declaration = u'<?xml version="1.0" encoding="{}"?>\n'.format
        self._xml_declaration_no_encoding = u'<?xml version="1.0"?>\n'
        self._format_doctype_empty = u'<!DOCTYPE {}>'.format
        self._format_doctype_public = u'<!DOCTYPE {} PUBLIC "{}">'.format
        self._format_doctype_system = u'<!DOCTYPE {} SYSTEM "{}">'.format
        self._format_doctype_public_system = u'<!DOCTYPE {} PUBLIC "{}" "{}">'.format
        self._quote = xml.sax.saxutils.quoteattr
        self._escape = xml.sax.saxutils.escape

    def _prepare_attr_value(self, value):
        return self._quote(value, self._entities)

    def _prepare_text(self, value):
        return self._escape(value, self._entities)

    def _prepare_child(self, child):
        return (
            child if isinstance(child, XMLFragment)
            else self._prepare_text(child)
        )

    def is_native_type(self, content):
        '''\
        Tests if an object of an type is to be decoded or converted to unicode
        or not.

        :param content: The object to test.
        :returns: :const:`True` for :class:`XMLFragment` instances,
            :const:`False` otherwise.
        '''
        return isinstance(content, XMLFragment)

    def element(self, name, children, attributes):
        '''\
        Creates an element string.

        :returns: The element created.
        :rtype: :class:`XMLFragment`
        '''
        name = self._prepare_text(name)
        attributes = self._join([
            self._format_attribute(
                self._prepare_text(attr_name),
                self._prepare_attr_value(attr_value)
            )
            for attr_name, attr_value in attributes.items()
        ])
        if len(children) == 0:
            return XMLFragment(self._format_element_empty(name, attributes))
        return XMLFragment(self._format_element(name, attributes,
            self._join([self._prepare_child(child) for child in children])
        ))

    def text(self, content):
        '''\
        Creates text string.

        :returns: The created text.
        :rtype: :class:`XMLFragment`
        '''
        return XMLFragment(self._prepare_text(content))

    def comment(self, content):
        '''\
        Creates a comment string.

        :returns: The created comment.
        :rtype: :class:`XMLFragment`
        '''
        return XMLFragment(self._format_comment(content))


    def processing_instruction(self, target, content):
        '''\
        Creates a processing instruction string.

        :returns: The created processing instruction.
        :rtype: :class:`XMLFragment`
        '''
        return XMLFragment(self._format_pi(target,
            u'' if content is None or len(content) == 0 else u' ' + content
        ))

    def document(self, doctype_name, doctype_publicid, doctype_systemid,
            children, omit_xml_declaration, encoding):
        '''\
        Creates a XML document.

        :returns: The created document.
        :rtype: :class:`XMLDocument`
        '''
        if omit_xml_declaration:
            xml_declaration = u''
        else:
            if encoding.upper() == u'UTF-8':
                xml_declaration = self._xml_declaration_no_encoding
            else:
                xml_declaration = self._format_xml_declaration(encoding)
        if doctype_name is None:
            doctype = u''
        elif doctype_publicid is None and doctype_systemid is None:
            doctype = self._format_doctype_empty(doctype_name)
        elif doctype_systemid is None:
            doctype = self._format_doctype_public(
                doctype_name, doctype_publicid)
        elif doctype_publicid is None:
            doctype = self._format_doctype_system(
                doctype_name, doctype_systemid)
        else:
            doctype = self._format_doctype_public_system(
                doctype_name, doctype_publicid, doctype_systemid)
        document = self._format_document(xml_declaration, doctype,
            self._join([self._prepare_child(child) for child in children])
        )
        return XMLDocument._create(document, encoding)


class XMLFragment(_unicode):
    '''\
    An XML Unicode string created by :class:`StringOutput`.
    '''


class XMLDocument(XMLFragment):
    '''\
    An Unicode string representing a XML document created by
    :class:`StringOutput`.
    '''
    __slots__ = ('_encoding', '_v_encoded')

    @classmethod
    def _create(cls, value, encoding):
        instance = XMLDocument(value)
        instance._encoding = encoding
        return instance

    @property
    def encoding(self):
        '''\
        The encoding of the document, is used if the byte string
        representation is received.
        '''
        return self._encoding

    @property
    def encoded(self):
        '''\
        The document encoded with :property:`encoding`, thus it is a byte
        string.

        The data of this property is created on first access, further
        retrieval of this property yields the same object.
        '''
        try:
            return self._v_encoded
        except AttributeError:
            self._v_encoded = self.encode(self._encoding)
            return self._v_encoded


del string, Output
