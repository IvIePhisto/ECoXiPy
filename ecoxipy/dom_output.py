# -*- coding: utf-8 -*-
ur'''\

:mod:`ecoxipy.dom_output` - DOM Creation
========================================

:class:`DOMOutput` creates `DOM <http://www.w3.org/DOM/>`_ (implemented in
Python by :mod:`xml.dom`) structures.


.. _ecoxipy.dom_output.examples:

Usage Example:

>>> from xml.dom.minidom import getDOMImplementation
>>> dom_br = getDOMImplementation().createDocument(None, 'br', None).documentElement
>>> dom_output = DOMOutput()
>>> doc = dom_output.document
>>> from ecoxipy import MarkupBuilder
>>> b = MarkupBuilder(dom_output)
>>> xml = b[:'section':True] (
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
...         attr='\'"<&>'
...     )
... )
>>> xml.toxml() == u"""<?xml version="1.0" ?><!DOCTYPE section><section attr="'&quot;&lt;&amp;&gt;"><p>Hello World!</p><p>äöüß</p><p>&lt;&amp;&gt;</p><raw/>text<br/>012345<br/><!--<This is a comment!>--><?pi-target <PI content>?><?pi-without-content ?></section>"""
True
'''

import xml.dom
import xml.dom.minidom

from . import Output


class DOMOutput(Output):
    '''\
    An :class:`Output` implementation which creates :mod:`xml.dom` nodes.

    :param document: The document to create DOM nodes with and to add those
        to.
    :type document: :class:`xml.dom.Document`
    :param dom_implementation: The DOM implementation to use to create a
        document, if ``document`` is :const:`None`. If this is :const:`None`,
        :func:`xml.dom.minidom.getDOMImplementation` is used.
    :type dom_implementation: :class:`xml.dom.DOMImplementation`
    '''
    def __init__(self, document=None, dom_implementation=None):
        if dom_implementation is None:
            dom_implementation = xml.dom.minidom.getDOMImplementation()
        self._dom_implementation = dom_implementation
        if document is None:
            document = self._dom_implementation.createDocument(None, None,
                None)
        self._document = document

    @property
    def document(self):
        '''The current :class:`xml.dom.Document`.'''
        return self._document

    def element(self, name, children, attributes):
        '''\
        Returns a DOM element representing the created element.

        :param name: The name of the element to create.
        :param children: The iterable of children to add to the element to
            create.
        :param attributes: The mapping of arguments of the element to create.
        :returns: The DOM element created.
        :rtype: :class:`xml.dom.Element`
        '''
        return _dom_create_element(self._document, name, attributes, children)

    def embed(self, content):
        '''\
        Imports the elements of ``content`` as XML and returns DOM nodes.

        :param content: The content to be embedded.
        :raises xml.parsers.expat.ExpatError: If a ``content`` element cannot
            be parsed.
        :returns:
            a list of :class:`xml.dom.Node` instances or a single instance

        ``content`` items will be treated as follows:

        *   :func:`str` and :func:`unicode` will be parsed as XML.
        *   :class:`xml.dom.Node` instances will be embedded.
        *   Other objects will be converted to :func:`unicode` and create
            text nodes.
        '''
        imported = self._document.childNodes.__class__()

        def import_xml(text):
            document = xml.dom.minidom.parseString(
                '<ROOT>{}</ROOT>'.format(text))
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
                if isinstance(content_item, unicode):
                    content_item = content_item.encode('UTF-8')
                if isinstance(content_item, str):
                    import_xml(content_item)
                else:
                    imported.append(self._document.createTextNode(
                        unicode(content_item)))
        if len(imported) == 1:
            return imported[0]
        return imported

    def text(self, content):
        '''\
        Creates DOM text nodes from the items of ``content``.

        :param content: The list of texts.
        :type content: :func:`list`
        :returns:
            A list of or a single text node.
        '''
        imported = self._document.childNodes.__class__()
        for content_item in content:
            imported.append(self._document.createTextNode(unicode(
                content_item)))
        if len(imported) == 1:
            return imported[0]
        return imported

    def comment(self, content):
        '''\
        Creates a DOM comment node.

        :param content: The content of the comment.
        :type content: :func:`str` or :func:`unicode`
        :returns:
            The created comment node.
        '''
        return self._document.createComment(content)

    def processing_instruction(self, target, content):
        '''\
        Creates a DOM processing instruction node.

        :param target: The target of the processing instruction.
        :type target: :func:`str` or :func:`unicode`
        :param content: The content of the processing instruction.
        :type content: :func:`str` or :func:`unicode`
        :returns:
            The created processing instruction node.
        '''
        return self._document.createProcessingInstruction(target, content)

    def document(self, doctype_name, doctype_publicid, doctype_systemid,
            children, omit_xml_declaration):
        '''\
        Creates a DOM document node.

        :param doctype_name:  The document element name.
        :type doctype_name: :func:`str`, :func:`unicode`, :const:`None`
        :param doctype_publicid:  The document type system ID.
        :type doctype_publicid: :func:`str`, :func:`unicode`, :const:`None`
        :param doctype_systemid:  The document type system ID.
        :type doctype_systemid: :func:`str`, :func:`unicode`, :const:`None`
        :param children: The list of children to add to the document to
            create.
        :type children: :func:`list`
        :param omit_xml_declaration: This is not honoured by this
            :class:`Output` implementation.
        :type omit_xml_declaration: :func:`bool`
        :returns:
            The created document node.
        '''
        if doctype_name is None:
            document = self._dom_implementation.createDocument(None,
                None, None)
        else:
            doctype = self._dom_implementation.createDocumentType(
                doctype_name, doctype_publicid, doctype_systemid)
            document = self._dom_implementation.createDocument(None,
                doctype_name, doctype)
        document.removeChild(document.documentElement)
        for child in children:
            document.appendChild(child)
            if child.nodeType == xml.dom.Node.ELEMENT_NODE:
                document.documentElement = child
        return document


def _dom_create_element(document, name, attributes, children):
    element = document.createElement(name)
    for name in attributes:
        element.setAttribute(unicode(name), unicode(attributes[name]))
    for child in children:
        if isinstance(child, xml.dom.Node):
            element.appendChild(child)
        else:
            element.appendChild(document.createTextNode(unicode(child)))
    document.documentElement = element
    return element


del Output
