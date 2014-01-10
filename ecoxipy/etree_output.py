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
>>> document_string = u"""<?xml version='1.0' encoding='utf-8'?>\\n<section attr="'&quot;&lt;&amp;&gt;"><p>Hello World!</p><p>äöüß</p><p>&lt;&amp;&gt;</p><raw />text<br />012345<!--<This is a comment!>--><?pi-target <PI content>?><?pi-without-content?></section>"""
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

    from collections import deque as _deque

    def is_native_type(self, content):
        '''\
        Tests if an object is a ``etree`` object by calling :meth:`iselement`
        of the element factory.

        :returns: :const:`True` for compatible :mod:`xml.etree.ElementTree`
            objects, :const:`False` otherwise.
        '''
        return self._element_factory.iselement(content)

    def element(self, name, children, attributes):
        '''\
        Creates an element.
        '''
        element = self._element_factory.Element(name, attributes)
        if len(children) < 2:
            try:
                child = children.popleft()
                if child.__class__ is _unicode:
                    element.text = child
                else:
                    element.append(child)
            except IndexError:
                pass
            return element
        texts = None
        previous = None
        def handle_texts():
            if texts is None or len(texts) == 0:
                return
            joined_texts = u''.join(texts)
            texts.clear()
            if previous is None:
                element.text = joined_texts
            else:
                previous.tail = joined_texts
        for child in children:
            if child.__class__ is _unicode:
                if texts is None:
                    texts = self._deque()
                texts.append(child)
            else:
                handle_texts()
                element.append(child)
                previous = child
        handle_texts()
        return element

    def text(self, content):
        '''\
        Creates an Unicode string.
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
        Creates an :mod:`xml.etree.ElementTree.ElementTree`-compatible object
        using the factory.

        As :mod:`xml.etree.ElementTree` lacks support for document type
        declarations, the ``doctype_*`` parameters are ignored. Element tree
        wrappers do not allow specification of the output encoding and of the
        XML declaration, so ``encoding`` and ``omit_xml_declaration`` are also
        ignored. As element trees only allow one root element, the length of
        ``children`` must be zero or one, otherwise a :class:`ValueError` is
        raised.
        '''
        if len(children) == 0:
            root_element = None
        elif len(children) > 1:
            raise ValueError('Only one root element is allowed.')
        else:
            root_element = children.popleft()
        return self._element_factory.ElementTree(root_element)


del Output
