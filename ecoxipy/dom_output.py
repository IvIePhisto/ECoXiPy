# -*- coding: utf-8 -*-
u'''\

:mod:`ecoxipy.dom_output` - DOM Creation
========================================

:class:`DOMOutput` creates `DOM <http://www.w3.org/DOM/>`_ (implemented in
Python by :mod:`xml.dom`) structures.


.. _ecoxipy.dom_output.examples:

Usage Example:

>>> from xml.dom.minidom import getDOMImplementation
>>> dom_br = getDOMImplementation().createDocument(None, 'br', None).documentElement
>>> dom_output = DOMOutput()
>>> from ecoxipy import MarkupBuilder
>>> b = MarkupBuilder(dom_output)
>>> xml_doc = b[:'section':True] (
...     b.section(
...         b.p(b & 'Hello World!'),
...         None,
...         b(u'<p>äöüß</p>'),
...         b.p('<&>'),
...         b(
...             '<raw/>text', b.br,
...             (i for i in range(3)), (i for i in range(3, 6)), dom_br
...         ),
...         b | '<This is a comment!>',
...         b['pi-target':'<PI content>'],
...         b['pi-without-content':],
...         attr='\\'"<&>'
...     )
... )
>>> val = xml_doc.toxml()
>>> document_string = u"""<?xml version="1.0" ?><!DOCTYPE section><section attr="'&quot;&lt;&amp;&gt;"><p>Hello World!</p><p>äöüß</p><p>&lt;&amp;&gt;</p><raw/>text<br/>012345<br/><!--<This is a comment!>--><?pi-target <PI content>?><?pi-without-content ?></section>"""
>>> for i in range(len(val)):
...     if val[i] != document_string[i]:
...         print(val[i:])
...         print()
...         print(document_string[i:])
...         break
>>> xml_doc.toxml() == document_string
True
'''

import xml.dom
import xml.dom.minidom

from ecoxipy import Output, InputEncodingMixin, _python3

if _python3:
    _prepare_xml_text = lambda text, in_encoding: (
        text.decode(in_encoding) if isinstance(text, bytes) else str(text))
else:
    _prepare_xml_text = lambda text, in_encoding: (
        text if isinstance(text, str) else unicode(text).encode('UTF-8'))


class DOMOutput(Output, InputEncodingMixin):
    '''\
    An :class:`Output` implementation which creates :mod:`xml.dom` nodes.

    :param document: The document to create DOM nodes with and to add those
        to.
    :type document: :class:`xml.dom.Document`
    :param dom_implementation: The DOM implementation to use to create a
        document, if ``document`` is :const:`None`. If this is :const:`None`,
        :func:`xml.dom.minidom.getDOMImplementation` is used.
    :type dom_implementation: :class:`xml.dom.DOMImplementation`
    :param in_encoding: Which encoding to use to decode byte strings.
    '''
    def __init__(self, document=None, dom_implementation=None,
            in_encoding='UTF-8'):
        if dom_implementation is None:
            dom_implementation = xml.dom.minidom.getDOMImplementation()
        self._dom_implementation = dom_implementation
        if document is None:
            document = self._dom_implementation.createDocument(None, None,
                None)
        self._document = document
        self._in_encoding = in_encoding

    @property
    def document(self):
        '''The current :class:`xml.dom.Document`.'''
        return self._document

    def element(self, name, children, attributes):
        '''\
        Returns a DOM element representing the created element.

        :returns: The DOM element created.
        :rtype: :class:`xml.dom.Element`
        '''
        element = self._document.createElement(name)
        for name in attributes:
            element.setAttribute(self.decode(name),
                self.decode(attributes[name]))
        for child in children:
            if isinstance(child, xml.dom.Node):
                element.appendChild(child)
            else:
                element.appendChild(self._document.createTextNode(
                    self.decode(child)))
        try:
            self._document.removeChild(self._document.documentElement)
        except xml.dom.NotFoundErr:
            pass
        self._document.appendChild(element)
        return element

    def embed(self, content):
        '''\
        Imports the elements of ``content`` as XML and returns DOM nodes.

        :raises xml.parsers.expat.ExpatError: If a ``content`` element cannot
            be parsed.
        :returns:
            a list of :class:`xml.dom.Node` instances or a single instance
        :rtype: :class:`xml.dom.NodeList`
        '''
        imported = self._document.childNodes.__class__()
        def import_xml(text):
            document = xml.dom.minidom.parseString(
                '<ROOT>' + text + '</ROOT>')
            doc_element = document.documentElement
            current_node = doc_element.firstChild
            while current_node is not None:
                next_node = current_node.nextSibling
                doc_element.removeChild(current_node)
                imported.append(current_node)
                current_node = next_node
            document.unlink()
        for content_item in content:
            if isinstance(content_item, xml.dom.Node):
                imported.append(content_item)
            else:
                import_xml(_prepare_xml_text(content_item, self.in_encoding))
        if len(imported) == 1:
            return imported[0]
        return imported

    def text(self, content):
        '''\
        Creates a DOM text node.

        :returns: The created text node.
        :rtype: :class:`xml.dom.Text`
        '''
        return self._document.createTextNode(self.decode(content))

    def comment(self, content):
        '''\
        Creates a DOM comment node.

        :returns: The created comment node.
        :rtype: :class:`xml.dom.Comment`
        '''
        return self._document.createComment(self.decode(content))

    def processing_instruction(self, target, content):
        '''\
        Creates a DOM processing instruction node.

        :returns: The created processing instruction node.
        :rtype: :class:`xml.dom.ProcessingInstruction`
        '''
        if content is None:
            content = u''
        else:
            content = self.decode(content)
        return self._document.createProcessingInstruction(
            self.decode(target), content)

    def document(self, doctype_name, doctype_publicid, doctype_systemid,
            children, omit_xml_declaration):
        '''\
        Creates a DOM document node.

        :returns: The created document node.
        :rtype: :class:`xml.dom.Document`
        '''
        if doctype_name is None:
            document = self._dom_implementation.createDocument(None,
                None, None)
        else:
            doctype_name = self.decode(doctype_name)
            doctype = self._dom_implementation.createDocumentType(
                doctype_name, doctype_publicid, doctype_systemid)
            document = self._dom_implementation.createDocument(None,
                doctype_name, doctype)
        document.removeChild(document.documentElement)
        for child in children:
            document.appendChild(child)
        return document


del Output, InputEncodingMixin
