# -*- coding: utf-8 -*-
'''\

:mod:`ecoxipy.parsing` - Parsing XML
====================================

This package contains :mod:`xml.sax` handlers to parse XML into
:class:`ecoxipy.MarkupBuilder` structures.


.. _ecoxipy.parsing.examples:

Examples
--------

>>> from ecoxipy.string_output import StringOutput
>>> output = StringOutput()
>>> handler = MarkupHandler(output)
>>> doc = handler.parse(b'<test><foo bar="test">Hello World!</foo></test>')
>>> print(doc)
<test><foo bar="test">Hello World!</foo></test>
>>> handler = XMLFragmentParser(output)
>>> fragment = handler.parse(u'<foo bar="test">Hello World!</foo><test/>')
>>> for item in fragment:
...     print(item)
<foo bar="test">Hello World!</foo>
<test/>

Classes
-------
'''

from io import BytesIO
from xml.sax import (SAXNotRecognizedException, SAXNotSupportedException,
    make_parser)
from xml.sax.handler import (ContentHandler, DTDHandler,
    property_lexical_handler)

from tinkerpy import LexicalHandler

from ecoxipy import _unicode

from ecoxipy._helpers import inherit_docstring



class MarkupHandler(ContentHandler, DTDHandler, LexicalHandler):
    '''\
    A SAX handler to create :mod:`ecoxipy` markup. By implementing your
    own :class:`ecoxipy.Output` class you can use it to parse XML.

    :param output: The output istance to use.
    :type output: :class:`ecoxipy.Output`
    '''
    def __init__(self, output):
        self._output = output
        self.reset()

    def reset(self):
        '''\
        Reset the current state. This should be called before parsing a new
        document after an exception occured while parsing. It is automatically
        called when a document has been processed in :meth:`endDocument`.
        '''
        self._doctype_name = None
        self._doctype_publicid = None
        self._doctype_systemid = None
        self._element_stack = []
        self._children_stack = []
        self._enter_node()

    def parse(self, source, parser=None):
        '''\
        Parses the given XML source and returns data in the representation
        of the :class:`ecoxipy.Output` instance given on creation.

        :param source: The XML source to parse. If this a byte string it will
            be wrapped into an :class:`io.BytesIO` instance. Then it is given
            to the ``parser``'s :meth:`xml.sax.xmlreader.XMLReader.parse`
            method.
        :param parser: The parser to use. If it is :const:`None`
            :func:`xml.sax.make_parser` is used to create one.
        :raises: :class:`xml.sax.SAXException` if the XML is not well-formed.
        :returns: the created XML data of the output representation.
        '''
        self.reset()
        if parser is None:
            parser = make_parser()
        parser.setContentHandler(self)
        parser.setDTDHandler(self)
        try:
            parser.setFeature(property_lexical_handler, self)
        except (SAXNotRecognizedException, SAXNotSupportedException):
            pass
        if isinstance(source, bytes):
            byte_stream = BytesIO(source)
            try:
                parser.parse(byte_stream)
            finally:
                byte_stream.close()
        else:
            parser.parse(source)
        document = self.document
        del self.document
        return document

    @property
    def document(self):
        '''\
        The document processed. This is only available after successfully
        parsing a XML document. This attribute is deletable but not
        assignable.
        '''
        return self._document

    @document.deleter
    def document(self):
        del self._document

    def _append_node(self, node):
        self._current_children.append(node)

    def _enter_node(self):
        self._current_children = []
        self._children_stack.append(self._current_children)

    def _leave_node(self, node):
        self._children_stack.pop()
        self._current_children = self._children_stack[-1]
        self._append_node(node)

    @inherit_docstring(DTDHandler)
    def notationDecl(self, name, publicId, systemId):
        self._doctype_name = _unicode(name)
        self._doctype_publicid = _unicode(publicId)
        self._doctype_systemid = _unicode(systemId)

    @inherit_docstring(DTDHandler)
    def unparsedEntityDecl(self, name, publicId, systemId, ndata):
        self.notationDecl(name, publicId, systemId)

    @inherit_docstring(ContentHandler)
    def startDocument(self):
        self._enter_node()

    @inherit_docstring(ContentHandler)
    def endDocument(self):
        self._document = self._output.document(self._doctype_name,
            self._doctype_publicid, self._doctype_systemid,
            self._children_stack[-1], True, 'UTF-8')
        self._leave_node(self._document)
        self.reset()

    @inherit_docstring(ContentHandler)
    def startElement(self, name, attrs):
        self._enter_node()
        self._element_stack.append((name, attrs))

    @inherit_docstring(ContentHandler)
    def endElement(self, name):
        _name, attrs = self._element_stack.pop()
        assert name == _name
        element = self._output.element(_unicode(name),
            self._current_children, {
            _unicode(attr_name): _unicode(attr_value)
            for attr_name, attr_value in attrs.items()
        })
        self._leave_node(element)

    @inherit_docstring(ContentHandler)
    def characters(self, content):
        text = self._output.text(_unicode(content))
        self._append_node(text)

    @inherit_docstring(ContentHandler)
    def ignorableWhitespace(self, content):
        return self.characters(content)

    @inherit_docstring(ContentHandler)
    def processingInstruction(self, target, data):
        pi = self._output.processing_instruction(_unicode(target),
            _unicode(data))
        self._append_node(pi)

    @inherit_docstring(LexicalHandler)
    def comment(self, content):
        comment = self._output.comment(_unicode(content))
        self._append_node(comment)



class XMLFragmentParsedException(Exception):
    '''\
    Indicates a XML fragment has been parsed by :class:`XMLFragmentParser`.
    '''
    def __init__(self, xml_fragment):
        self._xml_fragment = xml_fragment

    @property
    def xml_fragment(self):
        '''\
        The parsed XML fragment, a :func:`list` instance.
        '''
        return self._xml_fragment


class XMLFragmentParser(MarkupHandler):
    '''\
    A SAX handler to read create XML fragments (lists of XML nodes) from
    Unicode strings and output :mod:`ecoxipy` data. If used as a
    :class:`xml.sax.handler.ContentHandler` it raises a
    :class:`XMLFragmentParsedException` when the root element is closed.

    :param output: The instance to use for creating XML.
    :type output: :class:`ecoxipy.Output`
    :param parser: The parser to use. If it is :const:`None`
        :func:`xml.sax.make_parser` is used to create one.
    :type parser: :class:`xml.sax.xmlreader.XMLReader`
    '''
    def __init__(self, output, parser=None):
        MarkupHandler.__init__(self, output)
        if parser is None:
            parser = make_parser()
        self._parser = parser
        self._parser.setContentHandler(self)
        self._parser.setDTDHandler(self)
        try:
            self._parser.setFeature(property_lexical_handler, self)
        except (SAXNotRecognizedException, SAXNotSupportedException):
            pass

    @inherit_docstring(MarkupHandler)
    def endElement(self, name):
        if len(self._element_stack) == 1:
            xml_fragment = self._current_children
            self.reset()
            raise XMLFragmentParsedException(xml_fragment)
        MarkupHandler.endElement(self, name)

    def parse(self, xml_fragment):
        '''\
        Parses the given XML fragment and returns data in the representation
        of the :class:`ecoxipy.Output` instance given on creation.

        :param xml_fragment: The XML fragment to parse.
        :type xml_fragment: Unicode string
        :raises: :class:`xml.sax.SAXException` if the XML is not well-formed.
        :returns: the created XML data of the output representation.
        '''
        content_document = u'<ROOT>{}</ROOT>'.format(xml_fragment)
        content_document = content_document.encode('UTF-8')
        byte_stream = BytesIO(content_document)
        try:
            self._parser.parse(byte_stream)
        except XMLFragmentParsedException as e:
            return e.xml_fragment
        finally:
            byte_stream.close()

del ContentHandler, DTDHandler, LexicalHandler, inherit_docstring