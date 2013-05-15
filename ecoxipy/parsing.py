# -*- coding: utf-8 -*-
'''\

:mod:`ecoxipy.parsing` - Parsing XML
====================================

The package :mod:`ecoxipy.parsing` contains :mod:`xml.sax` handlers to parse
XML into :class:`ecoxipy.MarkupBuilder` structures.
'''

import io
import xml.sax
import xml.sax.handler

import tinkerpy

from ecoxipy import _unicode


class MarkupHandler(xml.sax.handler.ContentHandler,
        xml.sax.handler.DTDHandler, tinkerpy.LexicalHandler):
    '''\
    A SAX handler to create :module:`ecoxipy` markup. By implementing your
    own :class:`ecoxipy.Output` class you can use it to parse XML.

    :param output: The output istance to use.
    :type output: :class:`ecoxipy.Output`
    '''
    def __init__(self, output):
        self._output = output
        self.reset()

    def reset(self):
        '''\
        Reset the current state.
        '''
        self._doctype_name = None
        self._doctype_publicid = None
        self._doctype_systemid = None
        self._element_stack = []
        self._children_stack = []
        self._enter_node()

    @property
    def current_children(self):
        '''\
        The current child list. You should not modify it if you want to
        continue parsing.
        '''
        return self._current_children

    def _append_node(self, node):
        self._current_children.append(node)

    def _enter_node(self):
        self._current_children = []
        self._children_stack.append(self._current_children)

    def _leave_node(self, node):
        self._children_stack.pop()
        self._current_children = self._children_stack[-1]
        self._append_node(node)

    def notationDecl(self, name, publicId, systemId):
        self._doctype_name = _unicode(name)
        self._doctype_publicid = _unicode(publicId)
        self._doctype_systemid = _unicode(systemId)

    def unparsedEntityDecl(self, name, publicId, systemId, ndata):
        self.notationDecl(name, publicId, systemId)

    def startDocument(self):
        self._enter_node()

    def endDocument(self):
        document = self._output.document(self, doctype_name, doctype_publicid,
            doctype_systemid, self._children_stack.pop(), True, 'UTF-8')
        self._leave_node(document)

    def startElement(self, name, attrs):
        self._enter_node()
        self._element_stack.append((name, attrs))

    def endElement(self, name):
        _name, attrs = self._element_stack.pop()
        assert name == _name
        element = self._output.element(_unicode(name),
            self._current_children, {
            _unicode(attr_name): _unicode(attr_value)
            for attr_name, attr_value in attrs.items()
        })
        self._leave_node(element)

    def characters(self, content):
        text = self._output.text(_unicode(content))
        self._append_node(text)

    ignorableWhitespace = characters

    def processingInstruction(self, target, data):
        pi = self._output.processing_instruction(_unicode(target),
            _unicode(data))
        self._append_node(pi)

    def comment(self, content):
        comment = self._output.comment(_unicode(content))
        self._append_node(comment)


class XMLFragmentParsedException(Exception):
    '''\
    Indicates a XML fragment has been parsed by :class:`XMLFragmentParser`.
    '''
    pass


class XMLFragmentParser(MarkupHandler):
    '''\
    A SAX handler to read create XML fragments (lists of XML nodes) from
    Unicode strings and output :mod:`ecoxipy` data. It raises a
    :class:`XMLFragmentParsedException` when the root element is closed. Then,
    and only then, the property :property:`xml_fragment` does not raise an
    :class:`AttributeError` on retrieval.
    '''
    def __init__(self, output):
        MarkupHandler.__init__(self, output)
        self._parser = xml.sax.make_parser()
        self._parser.setContentHandler(self)
        self._parser.setDTDHandler(self)
        try:
            self._parser.setFeature(xml.sax.handler.property_lexical_handler,
                self)
        except (xml.sax.SAXNotRecognizedException,
                xml.sax.SAXNotSupportedException):
            pass

    def endElement(self, name):
        if len(self._element_stack) == 1:
            self._v_xml_fragment = self._current_children
            self.reset()
            raise XMLFragmentParsedException()
        MarkupHandler.endElement(self, name)

    @property
    def xml_fragment(self):
        '''\
        The parsed XML fragment, a :func:`list` instance. Only available
        if the root element was closed.
        '''
        return self._v_xml_fragment

    @xml_fragment.deleter
    def xml_fragment(self):
        del self._v_xml_fragment

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
        byte_stream = io.BytesIO(content_document)
        try:
            self._parser.parse(byte_stream)
        except XMLFragmentParsedException:
            parsed_fragment = self.xml_fragment
            del self.xml_fragment
            return parsed_fragment
        finally:
            byte_stream.close()

del tinkerpy