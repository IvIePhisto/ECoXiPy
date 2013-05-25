# -*- coding: utf-8 -*-
u'''\

:mod:`ecoxipy.pyxom.output` - PyXOM Structures
============================================================

:class:`PyXOMOutput` creates structures consisting of
:class:`ecoxipy.pyxom` data, which is an alternative to
:class:`xml.dom` structures.


.. _ecoxipy.pyxom.output.examples:

Examples
--------

Creating a document and retrieving the byte string:

>>> from ecoxipy import MarkupBuilder
>>> b = MarkupBuilder()
>>> document = b[:'section':True] (
...     b.article(
...         b.h1(
...             b & '<Example>', # Explicitly insert text
...             data='to quote: <&>"\\''
...         ),
...         b.p(
...             {'umlaut-attribute': u'äöüß'},
...             'Hello', b.em(' World', count=1), '!'
...         ),
...         None,
...         b.div(
...             # Insert elements with special names using subscripts:
...             b['data-element'](u'äöüß <&>'),
...             # Import content by calling the builder:
...             b(
...                 '<p attr="value">raw content</p>Some Text',
...                 # Create an element without calling the creating method:
...                 b.br,
...                 (i for i in range(3))
...             ),
...             (i for i in range(3, 6))
...         ),
...         b | '<This is a comment!>',
...         b['pi-target':'<PI content>'],
...         b['pi-without-content':],
...         lang='en'
...     )
... )
>>> document_string = u"""<!DOCTYPE section><article lang="en"><h1 data="to quote: &lt;&amp;&gt;&quot;'">&lt;Example&gt;</h1><p umlaut-attribute="äöüß">Hello<em count="1"> World</em>!</p><div><data-element>äöüß &lt;&amp;&gt;</data-element><p attr="value">raw content</p>Some Text<br/>012345</div><!--<This is a comment!>--><?pi-target <PI content>?><?pi-without-content?></article>"""
>>> bytes(document) == document_string.encode('UTF-8')
True

For more examples see :mod:`ecoxipy.pyxom`.


:class:`Output` Implementation
------------------------------

.. autoclass:: ecoxipy.pyxom.output.PyXOMOutput
'''

from ecoxipy import Output, _unicode

import ecoxipy.pyxom


class PyXOMOutput(Output):
    '''\
    An :class:`Output` implementation which creates
    :class:`ecoxipy.pyxom.XMLNode` instances and Unicode string instances.

    :param check_well_formedness: If :const:`True` the nodes will be checked
        for valid values.
    :type check_well_formedness: :func:`bool`
    '''
    def __init__(self, check_well_formedness=False):
        self._check_well_formedness = check_well_formedness

    @classmethod
    def is_native_type(self, content):
        '''\
        Tests if an object of an type is to be decoded or converted to Unicode
        or not.

        :param content: The object to test.
        :returns: :const:`True` for :`ecoxipy.pyxom.XMLNode` instances,
            :const:`False` otherwise.
        '''
        return isinstance(content, ecoxipy.pyxom.XMLNode)

    def element(self, name, children, attributes):
        '''\
        Returns a :class:`ecoxipy.pyxom.Element`.

        :returns: The element created.
        :rtype: :class:`ecoxipy.pyxom.Element`
        '''
        return ecoxipy.pyxom.Element(name, children, attributes,
            self._check_well_formedness)

    def text(self, content):
        '''\
        Creates a Unicode string.

        :returns: The created Unicode string.
        '''
        return ecoxipy.pyxom.Text(content)

    def comment(self, content):
        '''\
        Creates a :class:`ecoxipy.pyxom.Comment`.

        :returns: The created comment.
        :rtype: :class:`ecoxipy.pyxom.Comment`
        '''
        return ecoxipy.pyxom.Comment(content, self._check_well_formedness)

    def processing_instruction(self, target, content):
        '''\
        Creates a :class:`ecoxipy.pyxom.ProcessingInstruction`.

        :returns: The created processing instruction.
        :rtype: :class:`ecoxipy.pyxom.ProcessingInstruction`
        '''
        return ecoxipy.pyxom.ProcessingInstruction(target, content,
            self._check_well_formedness)

    def document(self, doctype_name, doctype_publicid, doctype_systemid,
            children, omit_xml_declaration, encoding):
        '''\
        Creates a :class:`ecoxipy.pyxom.Document` instance.

        :returns: The created document representation.
        :rtype: :class:`ecoxipy.pyxom.Document`
        '''
        return ecoxipy.pyxom.Document(doctype_name, doctype_publicid,
            doctype_systemid, children, omit_xml_declaration, encoding,
            self._check_well_formedness)

del Output
