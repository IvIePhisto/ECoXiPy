# -*- coding: utf-8 -*-
u'''\

:mod:`ecoxipy.string_output` - Building XML Strings
===================================================

:class:`StringOutput` creates strings of XML.


.. _ecoxipy.string_output.examples:

Usage Example:

>>> xml_output = StringOutput(check_well_formedness=True)
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

>>> from ecoxipy import XMLWellFormednessException
>>> def catch_not_well_formed(method, *args):
...     try:
...         return getattr(xml_output, method)(*args)
...     except XMLWellFormednessException as e:
...         print(e)
>>> t = catch_not_well_formed(u'document', u'1nvalid-xml-name', None, None, [], True, u'UTF-8')
The value "1nvalid-xml-name" is not a valid XML name.
>>> t = catch_not_well_formed(u'document', u'html', u'"', None, [], True, u'UTF-8')
The value "\\"" is not a valid document type public ID.
>>> t = catch_not_well_formed(u'document', u'html', None, u'"\\'', [], True, u'UTF-8')
The value "\\"'" is not a valid document type system ID.
>>> t = catch_not_well_formed(u'element', u'1nvalid-xml-name', [], {})
The value "1nvalid-xml-name" is not a valid XML name.
>>> t = catch_not_well_formed(u'element', u't', [], {u'1nvalid-xml-name': u'content'})
The value "1nvalid-xml-name" is not a valid XML name.
>>> t = catch_not_well_formed(u'processing_instruction', u'1nvalid-xml-name', None)
The value "1nvalid-xml-name" is not a valid XML processing instruction target.
>>> t = catch_not_well_formed(u'processing_instruction', u'target', u'invalid PI content ?>')
The value "invalid PI content ?>" is not a valid XML processing instruction content because it contains "?>".
>>> t = catch_not_well_formed(u'comment', u'invalid XML comment --')
The value "invalid XML comment --" is not a valid XML comment because it contains "--".
'''

from xml.sax.saxutils import quoteattr, escape

from ecoxipy import Output, _python2, _unicode, _helpers


class StringOutput(Output):
    '''\
    An :class:`ecoxipy.Output` implementation which creates XML as strings.

    :param entities: A mapping of characters to text to replace them with
        when escaping.
    :param check_well_formedness: The property
        :attr:`check_well_formedness` is determined by this value.
    :type check_well_formedness: :func:`bool`
    '''
    def __init__(self, entities=None, check_well_formedness=False):
        if entities is None:
            entities = {}
        self._entities = entities
        if bool(check_well_formedness):
            self._check_name = _helpers.enforce_valid_xml_name
            self._check_pi_target = _helpers.enforce_valid_pi_target
            self._check_pi_content = _helpers.enforce_valid_pi_content
            self._check_comment = _helpers.enforce_valid_comment
        else:
            nothing = lambda value: None
            self._check_name = nothing
            self._check_pi_target = nothing
            self._check_pi_content = nothing
            self._check_comment = nothing
        self._check_well_formedness = check_well_formedness
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
        self._format_doctype_system = u'<!DOCTYPE {} SYSTEM {}>'.format
        self._format_doctype_public_system = u'<!DOCTYPE {} PUBLIC "{}" {}>'.format
        self._format_doctype_systemid_quotes = u'"{}"'.format
        self._format_doctype_systemid_apos = u"'{}'".format

    @property
    def check_well_formedness(self):
        '''If :const:`True` the nodes will be checked for valid values.'''
        return self._check_well_formedness

    def _prepare_text(self, value):
        return escape(value, self._entities)

    def _prepare_attribute(self, name, value):
        self._check_name(name)
        return self._format_attribute(
            self._prepare_text(name),
            quoteattr(value, self._entities)
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
        :raises ecoxipy.XMLWellFormednessException: If
            :attr:`check_well_formedness` is :const:`True` and the
            ``name`` is not a valid XML name.
        '''
        self._check_name(name)
        name = self._prepare_text(name)
        attributes = self._join([
            self._prepare_attribute(attr_name, attr_value)
            for attr_name, attr_value in attributes.items()
        ])
        if len(children) == 0:
            return XMLFragment(self._format_element_empty(name, attributes))
        return XMLFragment(self._format_element(name, attributes,
            self._join([child for child in children])
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
        :raises ecoxipy.XMLWellFormednessException: If
            :attr:`check_well_formedness` is :const:`True` and
            ``content`` is not valid.
        '''
        self._check_comment(content)
        return XMLFragment(self._format_comment(content))


    def processing_instruction(self, target, content):
        '''\
        Creates a processing instruction string.

        :returns: The created processing instruction.
        :rtype: :class:`XMLFragment`
        :raises ecoxipy.XMLWellFormednessException: If
            :attr:`check_well_formedness` is :const:`True` and
            either the ``target`` or the ``content`` are not valid.
        '''
        self._check_pi_target(target)
        if content is not None:
            self._check_pi_content(content)
        return XMLFragment(self._format_pi(target,
            u'' if content is None or len(content) == 0 else u' ' + content
        ))

    def document(self, doctype_name, doctype_publicid, doctype_systemid,
            children, omit_xml_declaration, encoding):
        '''\
        Creates a XML document.

        :returns: The created document.
        :rtype: :class:`XMLDocument`
        :raises ecoxipy.XMLWellFormednessException: If
            :attr:`check_well_formedness` is :const:`True` and the
            document type's document element name is not a valid XML name,
            ``doctype_publicid`` is not a valid public ID or
            ``doctype_systemid`` is not a valid system ID.
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
        else:
            if doctype_systemid is not None:
                if u'"' in doctype_systemid:
                    systemid_creator = self._format_doctype_systemid_apos
                else:
                    systemid_creator = self._format_doctype_systemid_quotes
            self._check_name(doctype_name)
            if doctype_publicid is None and doctype_systemid is None:
                doctype = self._format_doctype_empty(doctype_name)
            elif doctype_systemid is None:
                if self._check_well_formedness:
                    _helpers.enforce_valid_doctype_publicid(
                        doctype_publicid)
                doctype = self._format_doctype_public(
                    doctype_name, doctype_publicid)
            elif doctype_publicid is None:
                if self._check_well_formedness:
                    _helpers.enforce_valid_doctype_systemid(
                        doctype_systemid)
                doctype = self._format_doctype_system(
                    doctype_name, systemid_creator(doctype_systemid))
            else:
                if self._check_well_formedness:
                    _helpers.enforce_valid_doctype_publicid(
                        doctype_publicid)
                    _helpers.enforce_valid_doctype_systemid(
                        doctype_systemid)
                doctype = self._format_doctype_public_system(
                    doctype_name, doctype_publicid,
                    systemid_creator(doctype_systemid))
        document = self._format_document(xml_declaration, doctype,
            self._join([child for child in children])
        )
        return XMLDocument._create(document, encoding)


class XMLFragment(_unicode):
    '''\
    An XML Unicode string created by :class:`StringOutput`.
    '''

    def __repr__(self):
        return u'ecoxipy.string_output.XMLFragment({})'.format(
            _unicode.__repr__(self))


class XMLDocument(XMLFragment):
    '''\
    An Unicode string representing a XML document created by
    :class:`StringOutput`.
    '''
    __slots__ = ('_encoding', '_v_encoded')

    def __repr__(self):
        return u'ecoxipy.string_output.XMLDocument({}, {})'.format(
            _unicode.__repr__(self), repr(self._encoding))

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
        The document encoded with :attr:`encoding`, thus it is a byte
        string.

        The data of this property is created on first access, further
        retrieval of this property yields the same object.
        '''
        try:
            return self._v_encoded
        except AttributeError:
            self._v_encoded = self.encode(self._encoding)
            return self._v_encoded


del Output
