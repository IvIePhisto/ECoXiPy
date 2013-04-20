# -*- coding: utf-8 -*-
ur'''\

:mod:`ecoxipy.dom_output` - DOM Creation
========================================

:class:`DOMOutput` creates `DOM <http://www.w3.org/DOM/>`_ (implemented in
Python by :mod:`xml.dom`) structures.


.. _ecoxipy.dom_output.examples:

Usage Example:

>>> dom_output = DOMOutput()
>>> doc = dom_output.document
>>> from ecoxipy import MarkupBuilder
>>> b = MarkupBuilder(dom_output)
>>> element = b.section(b.p('Hello World!'), None, b.p(u'äöüß'), b.p('<&>'), b('<raw/>text', b.br, (str(i) for i in range(3)), (str(i) for i in range(3, 6))), attr='\'"<&>')
>>> element.toxml() == u"""<section attr="'&quot;&lt;&amp;&gt;"><p>Hello World!</p><p>äöüß</p><p>&lt;&amp;&gt;</p><raw/>text<br/>012345</section>"""
True
'''

from xml import dom
from xml.dom import minidom

from . import Output, _dom_create_element


class DOMOutput(Output):
    '''An :class:`Output` implementation which creates :mod:`xml.dom` nodes.

    :param document: The document to create DOM nodes with and to add those
        to.
    :type document: :class:`xml.dom.Document`
    :param dom_implementation: The DOM implementation to use to create a
        document, if ``document`` is :const:`None`. If this is :const:`None`,
        :func:`xml.dom.minidom.getDOMImplementation` is used.
    :type dom_implementation: :class:`xml.dom.DOMImplementation`
    '''
    def __init__(self, document=None, dom_implementation=None):
        if document is None:
            if dom_implementation is None:
                dom_implementation = minidom.getDOMImplementation()
            document = dom_implementation.createDocument(None, None, None)
        self._document = document

    @property
    def document(self):
        '''The current :class:`xml.dom.Document`.'''
        return self._document

    def element(self, name, children, attributes):
        '''Returns a DOM element representing the created element.

        :param name: The name of the element to create.
        :type name: :func:`str`
        :param children: The iterable of children to add to the element to
            create.
        :param attributes: The mapping of arguments of the element to create.
        :returns: The DOM element created.
        :rtype: :class:`xml.dom.Element`
        '''
        return _dom_create_element(self._document, name, attributes, children)

    def embed(self, *content):
        '''Imports the elements of ``content`` as XML and returns DOM nodes.

        :param content: the XML to import
        :type content: :func:`str`, :func:`unicode` or :class:`xml.dom.Node`
        :raises xml.parsers.expat.ExpatError: If a ``content`` element cannot
            be parsed.
        :rtype: a list of class:`xml.dom.Node` instances or a single instance
        '''
        def embed_dom_node(node):
            def import_element(element):
                imported_element = self._document.createElement(
                    element.tagName)
                attributes = element.attributes
                for name, value in attributes.items():
                    imported_element.setAttribute(name, value)
                import_dom_nodes(
                    imported_element.childNodes, element.childNodes)
                return imported_element

            def import_text(text):
                return self._document.createTextNode(text.data)

            if node.nodeType == dom.Node.ELEMENT_NODE:
                return import_element(node)
            elif node.nodeType in [dom.Node.TEXT_NODE,
                    dom.Node.CDATA_SECTION_NODE]:
                return import_text(node)
            return None

        def import_dom_nodes(parentNodes, nodes):
            for node in nodes:
                imported_node = import_dom_node(node)
                if imported_node is not None:
                    parentNodes.append(imported_node)

        def import_xml(text):
            document = minidom.parseString('<ROOT>{}</ROOT>'.format(text))
            nodes = []
            if isinstance(document, self._document.__class__):
                for node in document.documentElement.childNodes:
                    if node.nodeType in supported_node_types:
                        nodes.append(node)
            else:
                import_dom_nodes(nodes, document.documentElement.childNodes)
            return nodes

        supported_node_types = (dom.Node.ELEMENT_NODE, dom.Node.TEXT_NODE,
            dom.Node.CDATA_SECTION_NODE)
        imported = self._document.childNodes.__class__()
        for content_element in content:
            if isinstance(content_element, unicode):
                content_element = content_element.encode('utf-8')
            if isinstance(content_element, str):
                imported.extend(import_xml(content_element))
            elif isinstance(content_element, dom.Node):
                if content_element.nodeType in supported_node_types:
                    imported.append(content_element)
        if len(imported) == 1:
            return imported[0]
        return imported
