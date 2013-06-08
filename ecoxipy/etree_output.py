# -*- coding: utf-8 -*-
u'''\

:mod:`ecoxipy.etree_output` - Building ElementTree Data
=======================================================

:class:`ETreeOutput` creates :mod:`xml.etree.ElementTree` structures.


.. _ecoxipy.etree_output.examples:

Usage Example:

>>> from xml.dom.minidom import getDOMImplementation
>>> etree_output = ETreeOutput()
>>> from ecoxipy import MarkupBuilder
>>> b = MarkupBuilder(etree_output)
>>> xml_doc = b[:'section':True] (
...     b.section(
...         b.p(b & 'Hello World!'),
...         None,
...         b(u'<p>äöüß</p>'),
...         b.p('<&>'),
...         b(
...             '<raw/>text', b.br,
...             (i for i in range(3)), (i for i in range(3, 6))
...         ),
...         b | '<This is a comment!>',
...         b['pi-target':'<PI content>'],
...         b['pi-without-content':],
...         attr='\\'"<&>'
...     )
... )
>>> from io import BytesIO
>>> bytes_io = BytesIO()
>>> xml_doc.write(bytes_io, 'utf-8', True)
>>> document_string = u"""<?xml version='1.0' encoding='utf-8'?>\\n<section attr="'&quot;&lt;&amp;&gt;"><p /><p /><p /><raw />text<br />012345<!--<This is a comment!>--><?pi-target <PI content>?><?pi-without-content?></section>"""
>>> bytes_io.getvalue() == document_string.encode('UTF-8')
True
'''

from ecoxipy import Output, _unicode


class ETreeOutput(Output):
    '''\
    An :class:`Output` implementation which creates
    :mod:`xml.etree.ElementTree` structures.

    :param element_factory: A :mod:`xml.etree.ElementTree`-compatible
        factory. If this is :const:`None` :mod:`xml.etree.ElementTree` is
        used.
    '''
    def __init__(self, element_factory=None):
        if element_factory is None:
            from xml.etree import ElementTree
            element_factory = ElementTree
        self._element_factory = element_factory

    def is_native_type(self, content):
        '''\
        Tests if an object of an type is to be decoded or converted to unicode
        or not.

        :param content: The object to test.
        :returns: :const:`True` for compatible :mod:`xml.etree.ElementTree` objects,
            :const:`False` otherwise.
        '''
        return self._element_factory.iselement(content)

    def element(self, name, children, attributes):
        '''\
        Creates an element.
        '''
        element = self._element_factory.Element(name, attributes)
        texts = []
        for child in children:
            if isinstance(child, _unicode):
                texts.append(child)
            else:
                if len(texts) > 0:
                    text = u''.join(texts)
                    texts = []
                    if len(element) == 0:
                        element.text = text
                    else:
                        element[-1].tail = text
                element.append(child)
        return element

    def text(self, content):
        '''\
        Creates a Unicode string.
        '''
        return content

    def comment(self, content):
        '''\
        Creates a comment element.
        '''
        return self._element_factory.Comment(content)

    def processing_instruction(self, target, content):
        '''\
        Creates a processing instruction element.
        '''
        return self._element_factory.ProcessingInstruction(
            target, content)

    def document(self, doctype_name, doctype_publicid, doctype_systemid,
            children, omit_xml_declaration, encoding):
        '''\
        Creates an :mod:`xml.etree.ElementTree.ElementTree`-compatible
        wrapper.

        As :mod:`xml.etree.ElementTree` lacks support for document type declarations the
        ``doctype_*`` parameters are ignored. Element tree wrappers do not
        allow specification of the output encoding and of the XML declaration,
        so ``encoding`` and ``omit_xml_declaration`` are also ignored. As
        element trees only allow one root element, the length of ``children``
        must be zero or one, otherwise a :class:`ValueError` is raised.
        '''
        if len(children) == 0:
            root_element = None
        elif len(children) > 1:
            raise ValueError('Only one root element is allowed.')
        else:
            root_element = children[0]
        return self._element_factory.ElementTree(root_element)


del Output
