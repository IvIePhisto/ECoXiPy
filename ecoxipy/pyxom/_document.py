# -*- coding: utf-8 -*-
from xml.sax.xmlreader import AttributesImpl

from ecoxipy import _python2, _unicode
from ecoxipy import _helpers

from ._common import XMLNode, ContainerNode, _string_repr
from ._content_nodes import Text


class DocumentType(object):
    '''\
    Represents a document type declaration of a :class:`Document`. It should
    not be instantiated on itself.

    :param name: The document element name.
    :type name: Unicode string
    :param publicid: The document type public ID or :const:`None`.
    :type publicid: Unicode string
    :param systemid: The document type system ID or :const:`None`.
    :type systemid: Unicode string
    :param check_well_formedness: If :const:`True` the document element name
        will be checked to be a valid XML name.
    :type check_well_formedness: :func:`bool`
    '''
    __slots__ = ('_name', '_publicid', '_systemid', '_check_well_formedness')

    def __init__(self, name, publicid, systemid, check_well_formedness):
        if check_well_formedness:
            if name is not None:
                _helpers.enforce_valid_xml_name(name)
            if publicid is not None:
                _helpers.enforce_valid_doctype_publicid(publicid)
            if systemid is not None:
                _helpers.enforce_valid_doctype_systemid(systemid)
        self._name = name
        self._publicid = publicid
        self._systemid = systemid
        self._check_well_formedness = check_well_formedness

    @property
    def name(self):
        '''\
        The document element name.
        '''
        return self._name

    @name.setter
    def name(self, name):
        if name is None:
            self._publicid = None
            self._systemid = None
        else:
            name = _unicode(name)
            if self._check_well_formedness:
                _helpers.enforce_valid_xml_name(name)
        self._name = name

    @property
    def publicid(self):
        '''\
        The document type public ID or :const:`None`
        '''
        return self._publicid

    @publicid.setter
    def publicid(self, publicid):
        if publicid is not None:
            publicid = _unicode(publicid)
            if self._check_well_formedness:
                _helpers.enforce_valid_doctype_publicid(publicid)
        self._publicid = publicid

    @property
    def systemid(self):
        '''\
        The document type system ID or :const:`None`
        '''
        return self._systemid

    @systemid.setter
    def systemid(self, systemid):
        if systemid is not None:
            systemid = _unicode(systemid)
            if self._check_well_formedness:
                _helpers.enforce_valid_doctype_systemid(systemid)
        self._systemid = systemid

    def __repr__(self):
        return 'ecoxipy.pyxom.DocumentType({}, {}, {})'.format(
            _string_repr(self._name),
            _string_repr(self._publicid),
            _string_repr(self._systemid),
        )

    def __eq__(self, other):
        return (isinstance(other, DocumentType)
            and self._name == other._name
            and self._publicid == other._publicid
            and self._systemid == other._systemid
        )

    def __ne__(self, other):
        return (not(isinstance(other, DocumentType))
            or self._name != other._name
            or self._publicid != other._publicid
            or self._systemid != other._systemid
        )


class Document(ContainerNode):
    '''\
    Represents a XML document.

    :param doctype_name: The document type root element name or :const:`None`
        if the document should not have document type declaration.
    :type doctype_name: Unicode string
    :param doctype_publicid: The public ID of the document type declaration
        or :const:`None`.
    :type doctype_publicid: Unicode string
    :param doctype_systemid: The system ID of the document type declaration
        or :const:`None`.
    :type doctype_systemid: Unicode string
    :param children: The document root :class:`XMLNode` instances.
    :param encoding: The encoding of the document. If it is :const:`None`
        `UTF-8` is used.
    :type encoding: Unicode string
    :param omit_xml_declaration: If :const:`True` the XML declaration is
        omitted.
    :type omit_xml_declaration: :func:`bool`
    :param check_well_formedness: If :const:`True` the document element name
        will be checked to be a valid XML name.
    :type check_well_formedness: :func:`bool`
    :raises ecoxipy.XMLWellFormednessException: If ``check_well_formedness``
        is :const:`True` and ``doctype_name`` is not a valid XML name,
        ``doctype_publicid`` is not a valid public ID or ``doctype_systemid``
        is not a valid system ID.
    '''
    __slots__ = ('_doctype', '_omit_xml_declaration', '_encoding')

    def __init__(self, doctype_name, doctype_publicid, doctype_systemid,
            children, omit_xml_declaration, encoding,
            check_well_formedness=False):
        ContainerNode.__init__(self, children)
        self._doctype = DocumentType(doctype_name, doctype_publicid,
            doctype_systemid, check_well_formedness)
        self._omit_xml_declaration = omit_xml_declaration
        if encoding is None:
            encoding = u'UTF-8'
        self._encoding = encoding

    @staticmethod
    def create(*children, **kargs):
        '''\
        Creates a document and converts parameters to appropriate types.

        :param children: The document root nodes. All items that are not
            :class:`XMLNode` instances create :class:`Text` nodes after they
            have been converted to Unicode strings.
        :param kargs: The parameters as the constructor has (except
            ``children``) are recognized. The items ``doctype_name``,
            ``doctype_publicid``, ``doctype_systemid``, and ``encoding`` are
            converted to Unicode strings if they are not :const:`None`.
            ``omit_xml_declaration`` is converted to boolean.
        :returns: The created document.
        :rtype: :class:`Document`
        :raises ecoxipy.XMLWellFormednessException: If ``doctype_name`` is not
            a valid XML name, ``doctype_publicid`` is not a valid public ID or
            ``doctype_systemid`` is not a valid system ID.
        '''
        doctype_name = kargs.get('doctype_name', None)
        if doctype_name is not None:
            doctype_name = _unicode(doctype_name)
        doctype_publicid = kargs.get('doctype_publicid', None)
        if doctype_publicid is not None:
            doctype_publicid = _unicode(doctype_publicid)
        doctype_systemid = kargs.get('doctype_systemid', None)
        if doctype_systemid is not None:
            doctype_systemid = _unicode(doctype_systemid)
        omit_xml_declaration = kargs.get('omit_xml_declaration', None)
        omit_xml_declaration = bool(omit_xml_declaration)
        encoding = kargs.get('encoding', None)
        if encoding is not None:
            encoding = _unicode(encoding)
        if len(children) == 0:
            import pdb; pdb.set_trace()
        return Document(doctype_name, doctype_publicid, doctype_systemid,
            [
                child if isinstance(child, XMLNode) else Text.create(child)
                for child in children
            ], omit_xml_declaration, encoding, True)

    @property
    def doctype(self):
        '''\
        The :class:`DocumentType` instance of the document or :const:`None`.
        '''
        return self._doctype

    @property
    def omit_xml_declaration(self):
        '''\
        If :const:`True` the XML declaration is omitted.
        '''
        return self._omit_xml_declaration

    @omit_xml_declaration.setter
    def omit_xml_declaration(self, value):
        self._omit_xml_declaration = bool(value)

    @property
    def encoding(self):
        '''\
        The encoding of the document.
        '''
        return self._encoding

    @encoding.setter
    def encoding(self, value):
        if value is not None:
            value = _unicode(value)
        else:
            value = u'UTF-8'
        self._encoding = value

    def __bytes__(self):
        '''\
        Creates a byte string containing the XML representation of the
        node with the encoding :meth:`encoding`.
        '''
        return self.create_str(encoding=self._encoding)

    if _python2:
        __str__ = __bytes__
        del __bytes__

    def __hash__(self):
        return object.__hash__(self)

    def create_sax_events(self, content_handler=None, out=None,
            out_encoding='UTF-8', indent_incr=None):
        return XMLNode.create_sax_events(self, content_handler, out,
            self._encoding, indent_incr)

    def _create_str(self, out):
        return out.document(self._doctype.name, self._doctype.publicid,
            self._doctype.systemid, [
                child._create_str(out) for child in self
            ], self._omit_xml_declaration, self._encoding)

    def _create_sax_events(self, content_handler, indent):
        content_handler.startDocument()
        try:
            notationDecl = content_handler.notationDecl
        except AttributeError:
            pass
        else:
            notationDecl(self._doctype.name, self._doctype.publicid,
                self._doctype.systemid)
        for child in self:
            child._create_sax_events(content_handler, indent)
        content_handler.endDocument()

    def __repr__(self):
        return 'ecoxipy.pyxom.Document[{}, {}, {}]'.format(
            repr(self._doctype),
            repr(self._omit_xml_declaration),
            _string_repr(self._encoding))

    def __eq__(self, other):
        if not(isinstance(other, Document)
                and self._doctype == other._doctype
                and self._omit_xml_declaration == other._omit_xml_declaration
                and self._encoding == other._encoding
                and len(self) == len(other)):
            return False
        for i in range(len(self)):
            if self[i] != other[i]:
                return False
        return True

    def __ne__(self, other):
        if (not(isinstance(other, Document))
                or self._doctype != other._doctype
                or self._omit_xml_declaration != other._omit_xml_declaration
                or self._encoding != other._encoding
                or len(self) != len(other)):
            return True
        for i in range(len(self)):
            if self[i] != other[i]:
                return True
        return False

    def duplicate(self):
        return Document(self._doctype.name, self._doctype.publicid,
            self._doctype.systemid,
            [child.duplicate() for child in self],
            self._omit_xml_declaration, self._encoding)
