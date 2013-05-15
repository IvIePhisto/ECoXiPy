# -*- coding: utf-8 -*-
u'''\

:mod:`ecoxipy.element_output` - Low-Footprint XML Structures
============================================================

:class:`ElementOutput` creates structures consisting of :class:`XMLNode`
instances, which are an immutable low-footprint alternative to what
:class:`ecoxipy.dom_output.DOMOutput`.


.. _ecoxipy.element_output.examples:

Examples
--------

Basic Usage:

>>> from ecoxipy import MarkupBuilder
>>> b = MarkupBuilder()
>>> doc = b[:'section':True] (
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


You can easily navigate the created instance structure:

>>> print(doc[0].name)
article
>>> print(doc[0]['lang'])
en
>>> doc[0]['lang'] is doc.children[0].attributes['lang']
True
>>> print(doc[0][0]['data'])
to quote: <&>"'


Getting the :func:`bytes` value of an document yields an encoded byte string:

>>> document_string = u"""<!DOCTYPE section><article lang="en"><h1 data="to quote: &lt;&amp;&gt;&quot;'">&lt;Example&gt;</h1><p umlaut-attribute="äöüß">Hello<em count="1"> World</em>!</p><div><data-element>äöüß &lt;&amp;&gt;</data-element><p attr="value">raw content</p>Some Text<br/>012345</div><!--<This is a comment!>--><?pi-target <PI content>?><?pi-without-content?></article>"""
>>> import sys
>>> (unicode(doc) if sys.version_info[0] < 3 else str(doc)) == document_string
True


Getting the :func:`bytes` value of an :class:`Document` creates a byte string
with the encoding specified on creation of the instance, it defaults
to "UTF-8":

>>> bytes(doc) == document_string.encode('UTF-8')
True


:class:`XMLNode` instances can also generate SAX events, see
:meth:`XMLNode.create_sax_events` (note that the default
:class:`xml.sax.ContentHandler` is :class:`xml.sax.saxutils.ContentHandler`,
which does not support comments):

>>> document_string = u"""<?xml version="1.0" encoding="UTF-8"?>\\n<article lang="en"><h1 data="to quote: &lt;&amp;&gt;&quot;'">&lt;Example&gt;</h1><p umlaut-attribute="äöüß">Hello<em count="1"> World</em>!</p><div><data-element>äöüß &lt;&amp;&gt;</data-element><p attr="value">raw content</p>Some Text<br></br>012345</div><?pi-target <PI content>?><?pi-without-content ?></article>"""
>>> if sys.version_info[0] > 2:
...     from io import StringIO
...     string_io = StringIO
... else:
...     from io import BytesIO
...     string_io = BytesIO
...     document_string = document_string.encode('UTF-8')
>>> string_out = string_io()
>>> content_handler = doc.create_sax_events(out=string_out)
>>> string_out.getvalue() == document_string
True
>>> string_out.close()


You can also create indented XML when calling the
:meth:`XMLNode.create_sax_events` by supplying the ``indent_incr`` argument:

>>> indented_document_string = u"""\\
... <?xml version="1.0" encoding="UTF-8"?>
... <article lang="en">
...     <h1 data="to quote: &lt;&amp;&gt;&quot;'">
...         &lt;Example&gt;
...     </h1>
...     <p umlaut-attribute="äöüß">
...         Hello
...         <em count="1">
...              World
...         </em>
...         !
...     </p>
...     <div>
...         <data-element>
...             äöüß &lt;&amp;&gt;
...         </data-element>
...         <p attr="value">
...             raw content
...         </p>
...         Some Text
...         <br></br>
...         012345
...     </div>
...     <?pi-target <PI content>?>
...     <?pi-without-content ?>
... </article>
... """
>>> if sys.version_info[0] <= 2:
...     indented_document_string = indented_document_string.encode('UTF-8')
>>> string_out = string_io()
>>> content_handler = doc.create_sax_events(indent_incr='    ', out=string_out)
>>> string_out.getvalue() == indented_document_string
True
>>> string_out.close()


:class:`Output` Implementation
------------------------------

.. autoclass:: ecoxipy.element_output.ElementOutput


Representation
--------------

.. autoclass:: ecoxipy.element_output.XMLNode

.. autoclass:: ecoxipy.element_output.Document
    :special-members: __getitem__

.. autoclass:: ecoxipy.element_output.DocumentType

.. autoclass:: ecoxipy.element_output.Element
    :special-members: __getitem__

.. autoclass:: ecoxipy.element_output.Comment

.. autoclass:: ecoxipy.element_output.ProcessingInstruction
'''

from abc import ABCMeta, abstractmethod
from collections import namedtuple
import xml.dom.minidom
import xml.sax.saxutils
import xml.sax.xmlreader

import tinkerpy

from ecoxipy import Output, _python3, _unicode
import ecoxipy.string_output


class ElementOutput(Output):
    '''\
    An :class:`Output` implementation which creates :class:`Element`
    instances and Unicode string instances.
    '''
    @classmethod
    def is_native_type(self, content):
        '''\
        Tests if an object of an type is to be decoded or converted to Unicode
        or not.

        :param content: The object to test.
        :returns: :const:`True` for :`XMLNode` instances, :const:`False`
            otherwise.
        '''
        return isinstance(content, XMLNode)

    def element(self, name, children, attributes):
        '''\
        Returns a :class:`Element`.

        :returns: The element created.
        :rtype: :class:`Element`
        '''
        return Element(name, children, attributes)

    def text(self, content):
        '''\
        Creates a Unicode string.

        :returns: The created Unicode string.
        '''
        return content

    def comment(self, content):
        '''\
        Creates a :class:`Comment`.

        :returns: The created comment.
        :rtype: :class:`Comment`
        '''
        return Comment(content)

    def processing_instruction(self, target, content):
        '''\
        Creates a :class:`ProcessingInstruction`.

        :returns: The created processing instruction.
        :rtype: :class:`ProcessingInstruction`
        '''
        return ProcessingInstruction(target, content)

    def document(self, doctype_name, doctype_publicid, doctype_systemid,
            children, omit_xml_declaration, encoding):
        '''\
        Creates a :class:`Document` instance.

        :returns: The created document representation.
        :rtype: :class:`Document`
        '''
        return Document(doctype_name, doctype_publicid, doctype_systemid,
            children, omit_xml_declaration, encoding)


class XMLNode(object):
    '''\
    Base class for XML node objects.

    Retrieving the byte string from an instance yields a byte string encoded
    as `UTF-8`.
    '''
    __metaclass__ = ABCMeta

    def __str__(self):
        '''\
        Creates a Unicode string containing the XML representation of
        the node.
        '''
        return self.create_str()

    def __bytes__(self):
        '''\
        Creates a byte string containing the XML representation of the
        node.
        '''
        return self.create_str(encoding='UTF-8')

    if not _python3:
        __unicode__ = __str__
        __str__ = __bytes__
        del __bytes__


    def create_str(self, out=None, encoding=None):
        '''\
        Creates a string containing the XML representation of the node.

        :param out: A :class:`ecoxipy.string_output.StringOutput` instance or
            :const:`None`. If it is the latter, a new
            :class:`ecoxipy.string_output.StringOutput` instance is created.
        :param encoding: The output encoding or :const:`None` for Unicode
            output. Is only taken into account if ``out`` is :const:`None`.
        '''
        if out is None:
            out = ecoxipy.string_output.StringOutput()
        output_string = self._create_str(out)
        if encoding is not None and not isinstance(output_string, bytes):
            output_string = output_string.encode(encoding)
        return output_string

    @abstractmethod
    def _create_str(self, out):
        '''\
        Creates a string containing the XML representation of the node.

        :param out: A :class:`ecoxipy.string_output.StringOutput` instance.
        '''
        pass

    def create_sax_events(self, content_handler=None, out=None,
            out_encoding='UTF-8', indent_incr=None):
        '''\
        Creates SAX events.

        :param content_handler: If this is :const:`None` a
            ``xml.sax.saxutils.XMLGenerator`` is created and used as the
            content handler. If in this case ``out`` is not :const:`None`,
            it is used for output.
        :type content_handler: :class:`xml.sax.ContentHandler`
        :param out: The output to write to if no ``content_handler`` is given.
            It should have a ``write`` method like files.
        :param out_encoding: The output encoding if no ``content_handler``
            is given and ``out`` is not :const:`None`.
        :param indent_incr: If this is not :const:`None` this activates
            pretty printing. In this case it should be a string and it is used
            for indenting.
        :type indent_incr: :func:`str`
        :returns: The content handler used.
        '''
        if content_handler is None:
            content_handler = xml.sax.saxutils.XMLGenerator(out, out_encoding)
        if indent_incr is None:
            indent = False
        else:
            indent_incr = _unicode(indent_incr)
            indent = (indent_incr, 0)
        self._create_sax_events(content_handler, indent)
        return content_handler

    @abstractmethod
    def _create_sax_events(self, content_handler, indent):
        pass


class Element(XMLNode):
    '''\
    Represents a XML element and is immutable.

    :param name: The name of the element to create.
    :param children: The children of the element.
    :type children: iterable of items
    :param attributes: The attributes of the element.
    :type attributes: subscriptable iterable over keys
    '''

    __slots__ = ('_name', '_children', '_attributes')

    def __init__(self, name, children, attributes):
        self._name = name
        self._children = tuple(children)
        self._attributes = tinkerpy.ImmutableDict(attributes)

    @property
    def name(self):
        '''The name of the element.'''
        return self._name

    @property
    def children(self):
        '''\
        A :func:`tuple` of the contained content (:class:`XMLNode`
        or Unicode string instances).
        '''
        return self._children

    @property
    def attributes(self):
        '''\
        An :class:`tinkerpy.ImmutableDict` instance containing the element's
        attributes. The key represents an attribute's name, the value is the
        attribute's value.
        '''
        return self._attributes

    def __getitem__(self, item):
        '''\
        Returns either the child with the index ``item``, if ``item`` is a
        :func:`int` instance, otherwise return the attribute with name
        ``item``.

        :param item: the child index or attribute name
        :type item: :func:`int` or a string
        :returns: the specified child or attribute
        :raises IndexError: if the child with index ``item`` does not exist
        :raises KeyError: if the attribute with name ``item`` does not exist
        '''
        if isinstance(item, int):
            return self._children[item]
        return self._attributes[item]

    def _create_str(self, out):
        return out.element(self.name, [
                    child._create_str(out)
                    if isinstance(child, XMLNode) else child
                for child in self.children
            ], self.attributes)

    def _create_sax_events(self, content_handler, indent):
        if indent:
            indent_incr, indent_count = indent
            child_indent = (indent_incr, indent_count + 1)
        else:
            child_indent = indent
        def do_indent(at_start=False):
            if indent:
                if indent_count > 0 or not at_start:
                    content_handler.characters('\n')
                for i in range(indent_count):
                    content_handler.characters(indent_incr)
        do_indent(True)
        attributes = xml.sax.xmlreader.AttributesImpl(self.attributes)
        content_handler.startElement(self.name, attributes)
        last_event_characters = False
        for child in self.children:
            if isinstance(child, XMLNode):
                child._create_sax_events(
                    content_handler, child_indent)
                last_event_characters = False
            else:
                if indent and not last_event_characters:
                    do_indent()
                    content_handler.characters(indent_incr)
                content_handler.characters(child)
                last_event_characters = True
        if len(self.children) > 0:
            do_indent()
        content_handler.endElement(self.name)
        if indent and indent_count == 0:
            content_handler.characters('\n')



class Comment(XMLNode):
    '''\
    Represent a comment.

    :param content: The comment content.
    '''
    __slots__ = ('_content')

    def __init__(self, content):
        self._content = content

    @property
    def content(self):
        return self._content

    def _create_str(self, out):
        return out.comment(self._content)

    def _create_sax_events(self, content_handler, indent):
        try:
            comment = content_handler.comment
        except AttributeError:
            return
        else:
            if indent:
                indent_incr, indent_count = indent
                content_handler.characters('\n')
                for i in range(indent_count):
                        content_handler.characters(indent_incr)
            comment(self._content)


class ProcessingInstruction(XMLNode):
    '''\
    Represent a processing instruction.

    :param target: The processing instruction target.
    :param content: The processing instruction content or :const:`None`.
    '''
    __slots__ = ('_target', '_content')

    def __init__(self, target, content):
        self._target = target
        self._content = content

    @property
    def target(self):
        return self._target

    @property
    def content(self):
        return self._content

    def _create_str(self, out):
        return out.processing_instruction(self._target, self._content)

    def _create_sax_events(self, content_handler, indent):
        if indent:
            indent_incr, indent_count = indent
            content_handler.characters('\n')
            for i in range(indent_count):
                    content_handler.characters(indent_incr)
        content_handler.processingInstruction(self.target,
            u'' if self._content is None else self._content)


'''\
Represents a document type declaration.
'''
DocumentType = namedtuple('DocumentType', 'name publicid systemid')


class Document(XMLNode):
    '''\
    Represents a XML document.

    :param doctype_name: The document type root element name or :const:`None`
        if the document should not have document type declaration.
    :param doctype_publicid: The public ID of the document type declaration.
    :param doctype_publicid: The system ID of the document type declaration.
    :param children: The document root nodes.
    :param encoding: The encoding of the document. If it is :const:`None`
        `UTF-8` is used.
    :param omit_xml_declaration: If :const:`True` the XML declaration is
        omitted.
    '''
    __slots__ = ('_doctype', '_children', '_omit_xml_declaration')

    def __init__(self, doctype_name, doctype_publicid, doctype_systemid,
            children, omit_xml_declaration, encoding):
        if doctype_name is None:
            self._doctype = None
        else:
            doctype_name = doctype_name
            self._doctype = DocumentType(doctype_name, doctype_publicid,
                doctype_systemid)
        self._children = children
        self._omit_xml_declaration = omit_xml_declaration
        if encoding is None:
            encoding = 'UTF-8'
        self._encoding = encoding

    @property
    def doctype(self):
        '''\
        The :class:`Doctype` instance of the document or :const:`None`.
        '''
        return self._doctype

    @property
    def omit_xml_declaration(self):
        '''\
        If :const:`True` the XML declaration is omitted.
        '''
        return self._omit_xml_declaration

    @property
    def encoding(self):
        '''\
        The encoding of the document.
        '''
        return self._doctype

    @property
    def children(self):
        '''\
        A :func:`tuple` of the document content nodes.
        '''
        return self._children

    def __bytes__(self):
        '''\
        Creates a byte string containing the XML representation of the
        node with the encoding :meth:`encoding`.
        '''
        return self.create_str(encoding=self._encoding)

    if not _python3:
        __str__ = __bytes__
        del __bytes__

    def __getitem__(self, item):
        '''\
        Returns the child with index ``item``.

        :param item: the child index
        :type item: :func:`int`
        :returns: the child with index ``item``
        :raises IndexError: if a child with index ``item`` does not exist
        '''
        return self._children[item]

    def create_sax_events(self, content_handler=None, out=None,
            out_encoding='UTF-8', indent_incr=None):
        '''\
        Creates SAX events.

        :param content_handler: If this is :const:`None` a
            ``xml.sax.saxutils.XMLGenerator`` is created and used as the
            content handler. If in this case ``out`` is not :const:`None`,
            it is used for output.
        :type content_handler: :class:`xml.sax.ContentHandler`
        :param out: The output to write to if no ``content_handler`` is given.
            It should have a ``write`` method like files.
        :param out_encoding: This is not taken into account, instead
            :meth:`encoding` is used  if no ``content_handler``
            is given and ``out`` is not :const:`None`.
        :param indent_incr: If this is not :const:`None` this activates
            pretty printing. In this case it should be a string and it is used
            for indenting.
        :type indent_incr: :func:`str`
        :returns: The content handler used.
        '''
        return XMLNode.create_sax_events(self, content_handler, out,
            self._encoding, indent_incr)

    def _create_str(self, out):
        return out.document(self._doctype.name, self._doctype.publicid,
            self._doctype.systemid, [
                    child._create_str(out)
                    if isinstance(child, XMLNode) else child
                for child in self.children
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
        for child in self._children:
            if isinstance(child, XMLNode):
                child._create_sax_events(content_handler, indent)
            else:
                content_handler.characters(child)
        content_handler.endDocument()


del ABCMeta, abstractmethod, namedtuple, Output
