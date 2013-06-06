# -*- coding: utf-8 -*-
u'''\

:mod:`ecoxipy.dom_output` - Building DOM Data
=============================================

:class:`DOMOutput` creates `*Document Object Model* (DOM)
<http://www.w3.org/DOM/>`_ (implemented in Python by :mod:`xml.dom`)
structures.


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
>>> document_string = u"""<?xml version="1.0" ?><!DOCTYPE section><section attr="'&quot;&lt;&amp;&gt;"><p>Hello World!</p><p>äöüß</p><p>&lt;&amp;&gt;</p><raw/>text<br/>012345<br/><!--<This is a comment!>--><?pi-target <PI content>?><?pi-without-content ?></section>"""
>>> xml_doc.toxml() == document_string
True
'''

from xml.dom import minidom, Node

from ecoxipy import Output


class DOMOutput(Output):
    '''\
    An :class:`Output` implementation which creates :mod:`xml.dom` nodes.

    :param dom_implementation: The DOM implementation to use to create
        :class:`xml.dom.Node` instances. If this is :const:`None`
        :func:`xml.dom.minidom.getDOMImplementation` is used.
    :type dom_implementation: :class:`xml.dom.DOMImplementation`
    '''
    def __init__(self, dom_implementation=None):
        if dom_implementation is None:
            dom_implementation = minidom.getDOMImplementation()
        self._dom_implementation = dom_implementation
        self._document = self._dom_implementation.createDocument(None, None,
                None)

    @classmethod
    def is_native_type(self, content):
        '''\
        Tests if an object of an type is to be decoded or converted to unicode
        or not.

        :param content: The object to test.
        :returns: :const:`True` for :`xml.dom.Node` instances, :const:`False`
            otherwise.
        '''
        return isinstance(content, Node)

    def element(self, name, children, attributes):
        '''\
        Returns a DOM element representing the created element.

        :returns: The DOM element created.
        :rtype: :class:`xml.dom.Element`
        '''
        element = self._document.createElement(name)
        for name in attributes:
            element.setAttribute(name, attributes[name])
        for child in children:
            element.appendChild(child)
        return element

    def text(self, content):
        '''\
        Creates a DOM text node.

        :returns: The created text node.
        :rtype: :class:`xml.dom.Text`
        '''
        return self._document.createTextNode(content)

    def comment(self, content):
        '''\
        Creates a DOM comment node.

        :returns: The created comment node.
        :rtype: :class:`xml.dom.Comment`
        '''
        return self._document.createComment(content)

    def processing_instruction(self, target, content):
        '''\
        Creates a DOM processing instruction node.

        :returns: The created processing instruction node.
        :rtype: :class:`xml.dom.ProcessingInstruction`
        '''
        if content is None:
            content = u''
        else:
            content = content
        return self._document.createProcessingInstruction(target, content)

    def document(self, doctype_name, doctype_publicid, doctype_systemid,
            children, omit_xml_declaration, encoding):
        '''\
        Creates a DOM document node.

        :returns: The created document node.
        :rtype: :class:`xml.dom.Document`
        '''
        if doctype_name is None:
            document = self._dom_implementation.createDocument(None,
                None, None)
        else:
            doctype_name = doctype_name
            doctype = self._dom_implementation.createDocumentType(
                doctype_name, doctype_publicid, doctype_systemid)
            document = self._dom_implementation.createDocument(None,
                doctype_name, doctype)
        document.removeChild(document.documentElement)
        for child in children:
            document.appendChild(child)
        return document


del Output
