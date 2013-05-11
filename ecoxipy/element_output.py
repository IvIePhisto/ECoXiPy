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


Getting the :func:`unicode` value in Python 2 or the :func:`str` value in
Python 3 of an :class:`XMLNode` creates a XML Unicode string:

>>> document_string = u"""<!DOCTYPE section><article lang="en"><h1 data="to quote: &lt;&amp;&gt;&quot;'">&lt;Example&gt;</h1><p umlaut-attribute="äöüß">Hello<em count="1"> World</em>!</p><div><data-element>äöüß &lt;&amp;&gt;</data-element><p attr="value">raw content</p>Some Text<br/>012345</div><!--<This is a comment!>--><?pi-target <PI content>?><?pi-without-content?></article>"""
>>> import sys
>>> (str(doc) if sys.version_info[0] > 2 else unicode(doc)) == document_string
True


Getting the :func:`bytes` value of an :class:`XMLNode` creates an `UTF-8`
encoded XML string:

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
    :special-members: __str__, __unicode__

.. autoclass:: ecoxipy.element_output.Document
    :special-members: __getitem__

.. autoclass:: ecoxipy.element_output.DocumentType

.. autoclass:: ecoxipy.element_output.Element
    :special-members: __getitem__

.. autoclass:: ecoxipy.element_output.Attributes

.. autoclass:: ecoxipy.element_output.Comment

.. autoclass:: ecoxipy.element_output.ProcessingInstruction
'''

from abc import ABCMeta, abstractmethod
from collections import namedtuple
import xml.dom.minidom
import xml.sax.saxutils
import xml.sax.xmlreader

import tinkerpy

from ecoxipy import Output, InputEncodingMixin, _python3, _unicode, _string_types
import ecoxipy.string_output


class ElementOutput(Output, InputEncodingMixin):
    '''\
    An :class:`Output` implementation which creates :class:`Element`
    instances and Unicode string instances.

    :param input_encoding: Which encoding to use to decode byte strings.
    '''
    def __init__(self, input_encoding='UTF-8'):
        self._input_encoding = input_encoding

    def element(self, name, children, attributes):
        '''\
        Returns a :class:`Element`.

        :returns: The element created.
        :rtype: :class:`Element`
        '''
        return Element(self.decode(name), children, attributes)

    def embed(self, content):
        '''\
        Parses the non-:class:`XMLNode` elements of ``content`` as XML and
        returns an a :func:`list` of :class:`Element` and :func:`unicode`
        instances or a single instance.

        :raises xml.parsers.expat.ExpatError: If XML is not well-formed.
        :returns:
            :class:`Element` or a :func:`list` of :class:`Element` instances
        :rtype: :func:`list`
        '''
        imported_content = []
        def import_xml(text):
            # TODO: use SAX for parsing
            def import_element(children_list, element):
                name = element.tagName
                children = []
                import_nodes(children, element.childNodes)
                attributes = import_attributes(element)
                imported_element = Element(name, children, attributes)
                children_list.append(imported_element)
            def import_text(children_list, text):
                children_list.append(text.data)
            def import_attributes(element):
                attributes = dict()
                for attr in element.attributes.values():
                    attributes[attr.name] = attr.value
                return attributes
            def import_comment(children_list, node):
                children_list.append(Comment(node.data))
            def import_processing_instruction(children_list, node):
                pi = ProcessingInstruction(node.target, node.data)
                children_list.append(pi)
            def import_nodes(children_list, nodes):
                for node in nodes:
                    if node.nodeType == xml.dom.Node.ELEMENT_NODE:
                        import_element(children_list, node)
                    elif node.nodeType in (xml.dom.Node.TEXT_NODE,
                            xml.dom.Node.CDATA_SECTION_NODE):
                        import_text(children_list, node)
                    elif (node.nodeType ==
                            xml.dom.Node.PROCESSING_INSTRUCTION_NODE):
                        import_processing_instruction(children_list, node)
                    elif (node.nodeType == xml.dom.Node.COMMENT_NODE):
                        import_comment(children_list, node)
            document = xml.dom.minidom.parseString(
                u'<ROOT>{}</ROOT>'.format(text))
            import_nodes(imported_content,
                document.documentElement.childNodes)
        for content_item in content:
            if isinstance(content_item, Element):
                imported_content.append(content_item)
            else:
                if isinstance(content_item, bytes):
                    content_item = content_item.decode(self._input_encoding)
                if not isinstance(content_item, _unicode):
                    content_item = _unicode(content_item)
                import_xml(content_item)
        if len(imported_content) == 1:
            return imported_content[0]
        return imported_content

    def text(self, content):
        '''\
        Creates a Unicode string.

        :returns: The created Unicode string.
        '''
        return self.decode(content)

    def comment(self, content):
        '''\
        Creates a :class:`Comment`.

        :returns: The created comment.
        :rtype: :class:`Comment`
        '''
        return Comment(self.decode(content))

    def processing_instruction(self, target, content):
        '''\
        Creates a :class:`ProcessingInstruction`.

        :returns: The created processing instruction.
        :rtype: :class:`ProcessingInstruction`
        '''
        return ProcessingInstruction(self.decode(target),
            None if content is None else self.decode(content))

    def document(self, doctype_name, doctype_publicid, doctype_systemid,
            children, omit_xml_declaration):
        '''\
        Creates a :class:`Document` instance.

        :returns: The created document representation.
        :rtype: :class:`Document`
        '''
        return Document(self.decode(doctype_name), doctype_publicid,
            doctype_systemid, children, omit_xml_declaration)


class XMLNode(object):
    '''\
    Base class for XML node objects.
    '''
    __metaclass__ = ABCMeta

    if _python3:
        def __str__(self):
            '''\
            Creates a Unicode string containing the XML representation of
            the node.

            :returns: The XML representation of the node as a :func:`str`
                instance.
            '''
            return self.create_str()

        def __bytes__(self):
            '''\
            Creates a byte string containing the XML representation of the
            node.

            :returns: The XML representation of the node as a :func:`bytes`
                instance with encoding `UTF-8`.
            '''
            return self.create_str(encoding='UTF-8')
    else:
        def __str__(self):
            '''\
            Creates a string containing the XML representation of the node.

            :returns: The XML representation of the node as a :func:`str`
                instance with encoding `UTF-8`.
            '''
            return self.create_str(encoding='UTF-8')

        def __unicode__(self):
            '''\
            Creates a Unicode string containing the XML representation of the
            node.

            :returns: The XML representation of the node as an :func:`unicode`
                instance.
            '''
            return self.create_str()

    def create_str(self, out=None, encoding=None):
        '''\
        Creates a string containing the XML representation of the node.

        :param out: A :class:`ecoxipy.string_output.StringOutput` instance or
            :const:`None`. If it is the latter, a new
            :class:`ecoxipy.string_output.StringOutput` instance is created.
        :param encoding: The output encoding or :const:`None` for
            Unicode output.
        '''
        if out is None:
            out = ecoxipy.string_output.StringOutput(out_encoding=encoding)
        return self._create_str(out, encoding)

    @abstractmethod
    def _create_str(self, out, encoding):
        '''\
        Creates a string containing the XML representation of the node.

        :param out: A :class:`ecoxipy.string_output.StringOutput` instance.
        :param encoding: The output encoding or :const:`None` for
            Unicode output.
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

    If the :func:`str` or :func:`unicode` functions are used on a
    :class:`Element` instance, a XML document encoded as a UTF-8 :func:`str`
    instance or :func:`unicode` instance respectively is returned.

    :param name: The name of the element to create. It's :func:`unicode` value
        will be used.
    :param children: The children of the element.
    :type children: iterable of items
    :param attributes: The attributes of the element.
    :type attributes: subscriptable iterable over keys
    :param decode: A callable with one argument which must return a Unicode
        string, should decode byte strings and retrieve the Unicode value
        of other value types.
    '''

    __slots__ = ('_name', '_children', '_attributes')

    def __init__(self, name, children, attributes,
            decode=lambda value:_unicode(value)):
        self._name = decode(name)
        self._children = tuple(children)
        self._attributes = Attributes(decode, attributes)

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
        An :class:`Attributes` instance containing the element's attributes.
        The key represents an attribute's name, the value is the attribute's
        value.
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

    def _create_str(self, out, encoding):
        return out.element(self.name, [
                    child._create_str(out, encoding)
                    if isinstance(child, XMLNode) else child
                for child in self.children
            ], self.attributes)

    def _create_sax_events(self, content_handler, indent):
        '''Creates SAX events for the element.'''
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
                content_handler.characters(_unicode(child))
                last_event_characters = True
        if len(self.children) > 0:
            do_indent()
        content_handler.endElement(self.name)
        if indent and indent_count == 0:
            content_handler.characters('\n')


class Attributes(tinkerpy.ImmutableDict):
    u'''\
    An immutable dictionary representing XML attributes. For attribute names
    (keys) and values their Unicode representation is used in all
    places.

    :param decode: A callable with one argument which must return a Unicode
        string, should decode byte strings and retrieve the Unicode value
        of other value types.
    :param args: Positional arguments conforming to :func:`dict`.
    :param kargs: Keyword arguments conforming to :func:`dict`.

    Usage examples:

    >>> import sys
    >>> if sys.version_info[0] > 2:
    ...     unicode = str
    >>> attrs = Attributes(unicode, {
    ...     'foo': 'bar', 'one': 1, u'äöüß': 'umlauts', 'umlauts': u'äöüß'
    ... })
    >>> print(attrs['umlauts'])
    äöüß
    >>> len(attrs)
    4
    >>> 'foo' in attrs
    True
    '''
    def __init__(self, decode, *args, **kargs):
        self._dict = dict(*args, **kargs)
        for name, value in self._dict.items():
            unicode_name = decode(name)
            unicode_value = decode(value)
            if not isinstance(name, _unicode):
                del self._dict[name]
            if value != unicode_value or unicode_name not in self._dict:
                self._dict[unicode_name] = unicode_value
        self._decode = decode

    def __getitem__(self, name):
        return tinkerpy.ImmutableDict.__getitem__(self, self._decode(name))


class Comment(XMLNode):
    '''\
    Represent a comment.

    :param content: The comment content.
    '''
    __slots__ = ('_content')

    def __init__(self, content):
        self._content = _unicode(content)

    @property
    def content(self):
        return self._content

    def _create_str(self, out, encoding):
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
        target = _unicode(target)
        if content is not None:
            content = _unicode(content)
        self._target = target
        self._content = content

    @property
    def target(self):
        return self._target

    @property
    def content(self):
        return self._content

    def _create_str(self, out, encoding):
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
    :param omit_xml_declaration: If :const:`True` the XML declaration is
        omitted.
    '''
    __slots__ = ('_doctype', '_children', '_omit_xml_declaration')

    def __init__(self, doctype_name, doctype_publicid, doctype_systemid,
            children, omit_xml_declaration):
        if doctype_name is None:
            self._doctype = None
        else:
            doctype_name = _unicode(doctype_name)
            self._doctype = DocumentType(doctype_name, doctype_publicid,
                doctype_systemid)
        self._children = children
        self._omit_xml_declaration = omit_xml_declaration

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
    def children(self):
        '''\
        A :func:`tuple` of the document content nodes.
        '''
        return self._children

    def __getitem__(self, item):
        '''\
        Returns the child with index ``item``.

        :param item: the child index
        :type item: :func:`int`
        :returns: the child with index ``item``
        :raises IndexError: if a child with index ``item`` does not exist
        '''
        return self._children[item]

    def _create_str(self, out, encoding):
        return out.document(self._doctype.name, self._doctype.publicid,
            self._doctype.systemid, [
                    child._create_str(out, encoding)
                    if isinstance(child, XMLNode) else child
                for child in self.children
            ], self._omit_xml_declaration)

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


del ABCMeta, abstractmethod, namedtuple, Output, InputEncodingMixin
