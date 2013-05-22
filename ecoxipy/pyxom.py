# -*- coding: utf-8 -*-
u'''\
PyXOM - Pythonic XML Object Model
=================================

This module implements a pythonic object model for the representation of XML
structures. To create PyXOM data conveniently use :mod:`ecoxipy.pyxom_output`.

Examples
--------

XML Creation
^^^^^^^^^^^^

If you use the constructors be sure to supply the right data types, otherwise
use the :meth:`create` methods or use :class:`ecoxipy.MarkupBuilder` which
take care of conversion.

>>> from ecoxipy import MarkupBuilder
>>> b = MarkupBuilder()
>>> document = Document.create(
...     b.article(
...         b.h1(
...             b & '<Example>',
...             data='to quote: <&>"\\''
...         ),
...         b.p(
...             {'umlaut-attribute': u'äöüß'},
...             'Hello', Element.create('em', ' World', count=1), '!'
...         ),
...         None,
...         b.div(
...             Element.create('data-element', Text.create(u'äöüß <&>')),
...             b(
...                 '<p attr="value">raw content</p>Some Text',
...                 b.br,
...                 (i for i in range(3))
...             ),
...             (i for i in range(3, 6))
...         ),
...         Comment.create('<This is a comment!>'),
...         ProcessingInstruction.create('pi-target', '<PI content>'),
...         ProcessingInstruction.create('pi-without-content'),
...         lang='en'
...     ), doctype_name='article', omit_xml_declaration=True
... )


Navigation
^^^^^^^^^^

Use list semantics to retrieve child nodes and attribute access to retrieve
node information:

>>> print(document.doctype.name)
article
>>> print(document[0].name)
article
>>> print(document[0].attributes['lang'])
en
>>> print(document[0][-2].target)
pi-target
>>> document[0][1].parent() is document[0]
True
>>> document[0][0] is document[0][1].previous() and document[0][1].next() is document[0][2]
True
>>> document.parent() is None and document[0].previous() is None and document[0].next() is None
True
>>> document[0].attributes.parent is document[0]
True


You can retrieve iterators for navigation through the tree:

>>> list(document[0][0].ancestors())
[ecoxipy.pyxom.Element('article', [...], {...}), ecoxipy.pyxom.Document(Doctype('article', None, None), [...], True, 'UTF-8')]
>>> list(document[0][1].descendants())
[ecoxipy.pyxom.Text('Hello'), ecoxipy.pyxom.Element('em', [...], {...}), ecoxipy.pyxom.Text(' World'), ecoxipy.pyxom.Text('!')]
>>> list(document[0][-1].preceding_siblings())
[ecoxipy.pyxom.ProcessingInstruction('pi-target', '<PI content>'), ecoxipy.pyxom.Comment('<This is a comment!>'), ecoxipy.pyxom.Element('div', [...], {...}), ecoxipy.pyxom.Element('p', [...], {...}), ecoxipy.pyxom.Element('h1', [...], {...})]
>>> list(document[0][2][-1].preceding())
[ecoxipy.pyxom.Text('4'), ecoxipy.pyxom.Text('3'), ecoxipy.pyxom.Text('2'), ecoxipy.pyxom.Text('1'), ecoxipy.pyxom.Text('0'), ecoxipy.pyxom.Element('br', [...], {...}), ecoxipy.pyxom.Text('Some Text'), ecoxipy.pyxom.Element('p', [...], {...}), ecoxipy.pyxom.Element('data-element', [...], {...}), ecoxipy.pyxom.Element('p', [...], {...}), ecoxipy.pyxom.Element('h1', [...], {...})]
>>> list(document[0][0].following_siblings())
[ecoxipy.pyxom.Element('p', [...], {...}), ecoxipy.pyxom.Element('div', [...], {...}), ecoxipy.pyxom.Comment('<This is a comment!>'), ecoxipy.pyxom.ProcessingInstruction('pi-target', '<PI content>'), ecoxipy.pyxom.ProcessingInstruction('pi-without-content', None)]
>>> list(document[0][1][0].following())
[ecoxipy.pyxom.Element('em', [...], {...}), ecoxipy.pyxom.Text('!'), ecoxipy.pyxom.Element('div', [...], {...}), ecoxipy.pyxom.Comment('<This is a comment!>'), ecoxipy.pyxom.ProcessingInstruction('pi-target', '<PI content>'), ecoxipy.pyxom.ProcessingInstruction('pi-without-content', None)]


Manipulation
^^^^^^^^^^^^

All :class:`XMLNode` instances have attributes which allow for modification.
:class:`Document` and :class:`Element` instances also allow modification of
their contents like sequences.

>>> document_copy = document.duplicate()
>>> document is document_copy
False
>>> document == document_copy
True
>>> old_data = document_copy[0][0].attributes.attr('data', 'foo bar')
>>> document_copy[0][0].attributes.attr('data', None) == u'foo bar'
True
>>> u'data' in document_copy[0][0].attributes
False
>>> document == document_copy
False
>>> document_copy[0][0].attributes.attr('data', old_data)
>>> u'data' in document_copy[0][0].attributes
True
>>> document == document_copy
True


XML Serialization
^^^^^^^^^^^^^^^^^

>>> document_string = u"""<!DOCTYPE article><article lang="en"><h1 data="to quote: &lt;&amp;&gt;&quot;'">&lt;Example&gt;</h1><p umlaut-attribute="äöüß">Hello<em count="1"> World</em>!</p><div><data-element>äöüß &lt;&amp;&gt;</data-element><p attr="value">raw content</p>Some Text<br/>012345</div><!--<This is a comment!>--><?pi-target <PI content>?><?pi-without-content?></article>"""

Getting the Unicode value of an document yields the XML document serialized as
an Unicode string:

>>> import sys
>>> if sys.version_info[0] < 3:
...     unicode(document) == document_string
... else:
...     str(document) == document_string
True


Getting the :func:`bytes` value of an :class:`Document` creates a byte string
of the serialized XML with the encoding specified on creation of the instance,
it defaults to "UTF-8":

>>> bytes(document) == document_string.encode('UTF-8')
True


:class:`XMLNode` instances can also generate SAX events, see
:meth:`XMLNode.create_sax_events` (note that the default
:class:`xml.sax.ContentHandler` is :class:`xml.sax.saxutils.ContentHandler`,
which does not support comments):

>>> document_string = u"""<?xml version="1.0" encoding="UTF-8"?>\\n<article lang="en"><h1 data="to quote: &lt;&amp;&gt;&quot;'">&lt;Example&gt;</h1><p umlaut-attribute="äöüß">Hello<em count="1"> World</em>!</p><div><data-element>äöüß &lt;&amp;&gt;</data-element><p attr="value">raw content</p>Some Text<br></br>012345</div><?pi-target <PI content>?><?pi-without-content ?></article>"""
>>> import sys
>>> from io import BytesIO
>>> string_out = BytesIO()
>>> content_handler = document.create_sax_events(out=string_out)
>>> string_out.getvalue() == document_string.encode('UTF-8')
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
>>> string_out = BytesIO()
>>> content_handler = document.create_sax_events(indent_incr='    ', out=string_out)
>>> string_out.getvalue() == indented_document_string.encode('UTF-8')
True
>>> string_out.close()


Classes
-------
'''

import abc
import ast
import collections
import xml.sax
import xml.sax.xmlreader
import xml.sax.saxutils

from ecoxipy import _python2, _unicode
import ecoxipy.string_output


class XMLNode(object):
    '''\
    Base class for XML node objects.

    Retrieving the byte string from an instance yields a byte string encoded
    as `UTF-8`.
    '''
    __metaclass__ = abc.ABCMeta
    __slots__ = ('_parent', '_next', '_previous')

    def _attribute_node(self, attribute):
        try:
            return getattr(self, attribute)
        except AttributeError:
            return None

    def parent(self):
        '''\
        The parent :class:`ContainerNode` or :const:`None` if the node has no
        parent.
        '''
        return self._attribute_node('_parent')

    def previous(self):
        '''\
        The previous :class:`XMLNode` or :const:`None` if the node has no
        preceding sibling.
        '''
        return self._attribute_node('_previous')

    def next(self):
        '''\
        The next :class:`XMLNode` or :const:`None` if the node has no
        following sibling.
        '''
        return self._attribute_node('_next')

    def _attribute_iterator(self, attribute):
        def iterator(current):
            while True:
                current = current._attribute_node(attribute)
                if current is None:
                    break
                else:
                    yield current
        return iterator(self)

    def ancestors(self):
        '''\
        Returns an iterator over all ancestors.
        '''
        return self._attribute_iterator('_parent')

    def preceding_siblings(self):
        '''\
        Returns an iterator over all preceding siblings.
        '''
        return self._attribute_iterator('_previous')

    def following_siblings(self):
        '''\
        Returns an iterator over all following siblings.
        '''
        return self._attribute_iterator('_next')

    def _attribute_climbing_iterator(self, attribute):
        siblings = self._attribute_iterator(attribute)
        for sibling in siblings:
            yield sibling
        parent = self.parent()
        if parent is not None:
            for parent_sibling in parent._attribute_climbing_iterator(
                    attribute):
                yield parent_sibling

    def preceding(self):
        '''\
        Returns an iterator over all preceding nodes.
        '''
        return self._attribute_climbing_iterator('_previous')

    def following(self):
        '''\
        Returns an iterator over all following nodes.
        '''
        return self._attribute_climbing_iterator('_next')

    def create_str(self, out=None, encoding='UTF-8'):
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
        if encoding is not None:
            output_string = output_string.encode(encoding)
        return output_string

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
        :param out_encoding: The output encoding or :const:`None` for
            Unicode output.
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

    def __str__(self):
        return self.create_str(encoding=None)

    def __bytes__(self):
        return self.create_str(encoding='UTF-8')

    if _python2:
        __unicode__ = __str__
        __str__ = __bytes__
        del __bytes__

    @abc.abstractmethod
    def duplicate(self, test=None):
        '''\
        Return a deep copy of the XML node, and its descendants if it is a
        :class:`ContainerNode` instance.
        '''

    @abc.abstractmethod
    def _create_str(self, out):
        pass

    @abc.abstractmethod
    def _create_sax_events(self, content_handler, indent):
        pass

    @abc.abstractmethod
    def __repr__(self):
        pass

    @abc.abstractmethod
    def __eq__(self, other):
        pass

    @abc.abstractmethod
    def __ne__(self, other):
        pass


class ContainerNode(XMLNode, collections.MutableSequence):
    __slots__ = ('_children', '_indexes')

    def __init__(self, children):
        self._children = children
        self._indexes = {}
        for i, child in enumerate(children):
            self._indexes[id(child)] = i
            child._parent = self
            if i > 0:
                self._wire_neighbors(previous, child)
            previous = child

    def children(self, reverse=False):
        '''\
        Returns an iterator over the children.

        :param reverse: If this is :const:`True` the children are returned in
            reverse document order.
        :returns: An iterator over the children.
        '''
        return self._children_rec(reverse)

    def descendants(self, reverse=False):
        '''\
        Returns an iterator over all descendants.

        :param reverse: If this is :const:`True` the descendants are returned
            in reverse document order.
        :returns: An iterator over the descendants.
        '''
        return self._descendants_rec(reverse)

    def _children_rec(self, reverse):
        def iterator():
            for child in (reversed(self) if reverse else self):
                yield child
        return iterator()

    def _descendants_rec(self, reverse):
        def iterator():
            for child in self._children_rec(reverse):
                yield child
                if isinstance(child, ContainerNode):
                    for descendant in child._descendants_rec(reverse):
                        yield descendant
        return iterator()

    def _unwire_child(self, child):
        del child._parent
        del child._next
        del child._previous
        del self._indexes[id(child)]

    def _wire_neighbors(self, left, right):
        left._next = right
        right._previous = left

    def _wire_child(self, index, child):
        old_parent = child.parent
        if old_parent is not None:
            old_parent.remove(child)
        child._parent = self
        self._indexes[child] = i
        if len(self) > 1:
            if index > 0:
                self._wire_neighbors(self[index-1], child)
            if index < len(self) - 1:
                self._wire_neighbors(child, self[index+1])

    def __getitem__(self, index):
        return self._children[index]

    def __len__(self):
        return len(self._children)

    def __iter__(self):
        return self._children.__iter__()

    def __contains__(self, child):
        return child in self._indexes

    def __reversed__(self):
        return self._children.__reversed__()

    def __setitem__(self, index, child):
        try:
            old_child = self._children[index]
        except IndexError:
            old_child = None
        self._children[index] = child
        if old_child is not None:
            self._unwire_child(old_child)
        self._wire_child(index, child)

    def insert(self, index, child):
        self._children.insert(index, child)
        self._wire_child(index, child)

    def __delitem__(self, index):
        child = self._children[index]
        del self._children[index]
        self._unwire_child(child)

    def remove(self, child):
        index = self._indexes[id(child)]
        del self[index]

    def __call__(self, *path):
        return Finder.find(self, path)


class Document(ContainerNode):
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
    __slots__ = ('_doctype', '_omit_xml_declaration', '_encoding')

    DocumentType = collections.namedtuple('DocumentType',
        'name publicid systemid')
    '''\
    Represents a document type declaration.

    :param name: The document element name.
    :param publicid: The document type public ID.
    :param systemid: The document type system ID.
    '''

    def __init__(self, doctype_name, doctype_publicid, doctype_systemid,
            children, omit_xml_declaration, encoding):
        ContainerNode.__init__(self, children)
        if doctype_name is None:
            self._doctype = None
        else:
            doctype_name = doctype_name
            self._doctype = self.DocumentType(doctype_name, doctype_publicid,
                doctype_systemid)
        self._omit_xml_declaration = omit_xml_declaration
        if encoding is None:
            encoding = 'UTF-8'
        self._encoding = encoding

    @staticmethod
    def create(*children, **kargs):
        doctype_name = kargs.get('doctype_name', None)
        if doctype_name is not None:
            doctype_name = _unicode(doctype_name)
        doctype_publicid = kargs.get('doctype_publicid', None)
        if doctype_publicid is not None:
            doctype_publicid = _unicode(doctype_publicid)
        doctype_systemid = kargs.get('doctype_systemid', None)
        if doctype_systemid is not None:
            doctype_systemid = _unicode(doctype_systemid)
        omit_xml_declaration = kargs.get('omit_xml_declaration', None)
        omit_xml_declaration = bool(omit_xml_declaration)
        encoding = kargs.get('encoding', None)
        if encoding is not None:
            encoding = _unicode(encoding)
        if len(children) == 0:
            import pdb; pdb.set_trace()
        return Document(doctype_name, doctype_publicid, doctype_systemid,
            [
                child if isinstance(child, XMLNode) else Text.create(child)
                for child in children
            ], omit_xml_declaration, encoding)

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

    @omit_xml_declaration.setter
    def omit_xml_declaration(self, value):
        self._omit_xml_declaration = value

    @property
    def encoding(self):
        '''\
        The encoding of the document.
        '''
        return self._encoding

    @encoding.setter
    def encoding(self, value):
        self._encoding = value

    def __bytes__(self):
        '''\
        Creates a byte string containing the XML representation of the
        node with the encoding :meth:`encoding`.
        '''
        return self.create_str(encoding=self._encoding)

    if _python2:
        __str__ = __bytes__
        del __bytes__

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
                child._create_str(out) for child in self
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
        for child in self:
            child._create_sax_events(content_handler, indent)
        content_handler.endDocument()

    def __repr__(self):
        return 'ecoxipy.pyxom.Document(Doctype(\'{}\', {}, {}), [...], {}, \'{}\')'.format(
            self._doctype.name.encode('unicode_escape').decode(),
            'None' if self._doctype.publicid is None
            else "'{}'".format(_unicode(self._doctype.publicid).encode(
                'unicode_escape').decode()),
            'None' if self._doctype.systemid is None
            else "'{}'".format(_unicode(self._doctype.systemid).encode(
                'unicode_escape').decode()),
            repr(self._omit_xml_declaration),
            self._encoding.encode('unicode_escape').decode())

    def __eq__(self, other):
        if not(isinstance(other, Document)
                and self._doctype == other._doctype
                and self._omit_xml_declaration == other._omit_xml_declaration
                and self._encoding == other._encoding
                and len(self) == len(other)):
            return False
        for i in range(len(self)):
            if self[i] != other[i]:
                return False
        return True

    def __ne__(self, other):
        if (not(isinstance(other, Document))
                or self._doctype != other._doctype
                or self._omit_xml_declaration != other._omit_xml_declaration
                or self._encoding == other._encoding
                or len(self) != len(other)):
            return True
        for i in range(len(self)):
            if self[i] != other[i]:
                return True
        return False

    def duplicate(self):
        return Document(self._doctype.name, self._doctype.publicid,
            self._doctype.systemid,
            [child.duplicate() for child in self],
            self._omit_xml_declaration, self._encoding)


class Attributes(dict):
    '''\
    Represents the attributes of an :class:`Element`. It should not be
    instantiated on itself.
    '''
    @property
    def parent(self):
        '''\
        The parent :class:`Element`.
        '''
        return self._parent

    def attr(self, name, value=False):
        '''\
        Allows for getting, setting and deleting attributes. The name and
        possible value are automatically converted to Unicode strings.

        :param name: The name of the attribute.
        :param value: :const:`False` for retrieval, :const:`None` for
            deletion and other types for setting the attribute.
        :returns: The attribute value (before setting or deletion if
            applicable) or :const:`None` if it does not exist.
        :raises KeyError: If the attribute is not defined on retrieval or
            deletion.
        '''
        name = _unicode(name)
        try:
            current_value = self[name]
        except KeyError:
            if value is False or value is None:
                raise
            current_value = None
        if value is None:
            del self[name]
        elif value is not False:
            value = _unicode(value)
            self[name] = value
        return current_value


class Element(ContainerNode):
    '''\
    Represents a XML element.

    :param name: The name of the element to create.
    :param children: The children of the element.
    :type children: iterable of items
    :param attributes: The attributes of the element.
    :type attributes: subscriptable iterable over keys
    '''
    __slots__ = ('_name', '_attributes')

    def __init__(self, name, children, attributes):
        ContainerNode.__init__(self, children)
        self._name = name
        self._attributes = Attributes(attributes)
        self._attributes._parent = self

    @staticmethod
    def create(name, *children, **attributes):
        return Element(_unicode(name),
            [
                child if isinstance(child, XMLNode) else Text.create(child)
                for child in children
            ], {
                _unicode(attr_name): _unicode(attr_value)
                for attr_name, attr_value in attributes.items()
            })

    @property
    def name(self):
        '''The name of the element.'''
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def attributes(self):
        '''\
        An :func:`dict` containing the element's attributes. The key
        represents an attribute's name, the value is the attribute's value.
        '''
        return self._attributes

    def _create_str(self, out):
        return out.element(self.name, [
                child._create_str(out) for child in self
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
                    content_handler.characters(u'\n')
                for i in range(indent_count):
                    content_handler.characters(indent_incr)
        do_indent(True)
        attributes = xml.sax.xmlreader.AttributesImpl(self.attributes)
        content_handler.startElement(self.name, attributes)
        last_event_characters = False
        for child in self:
            if isinstance(child, Text):
                if indent and not last_event_characters:
                    do_indent()
                    content_handler.characters(indent_incr)
                child._create_sax_events(content_handler, child_indent)
                last_event_characters = True
            else:
                child._create_sax_events(content_handler, child_indent)
                last_event_characters = False
        if len(self) > 0:
            do_indent()
        content_handler.endElement(self.name)
        if indent and indent_count == 0:
            content_handler.characters(u'\n')

    def __repr__(self):
        return 'ecoxipy.pyxom.Element(\'{}\', [...], {{...}})'.format(
            self._name.encode('unicode_escape').decode())

    def __eq__(self, other):
        if not(isinstance(other, Element)
                and self._name == other._name
                and self._attributes == other._attributes
                and len(self) == len(other)):
            return False
        for i in range(len(self)):
            if self[i] != other[i]:
                return False
        return True

    def __ne__(self, other):
        if (not(isinstance(other, Element))
                or self._name != other._name
                or self._attributes != other._attributes
                or len(self) != len(other)):
            return True
        for i in range(len(self)):
            if self[i] != other[i]:
                return True
        return False

    def duplicate(self):
        return Element(self._name,
            [child.duplicate() for child in self],
            {name: value for name, value in self._attributes.items()})


class ContentNode(XMLNode):
    '''\
    Represents a node with content.

    :param content: The content.
    '''
    __slots__ = ('_content')

    def __init__(self, content):
        self._content = content

    @classmethod
    def create(cls, content):
        return cls(_unicode(content))

    @property
    def content(self):
        return self._content

    @content.setter
    def content(self, value):
        self._content = value

    def __eq__(self, other):
        return (isinstance(other, self.__class__)
            and self._content == other._content)

    def __ne__(self, other):
        return (not(isinstance(other, self.__class__))
            or self._content != other._content)


class Text(ContentNode):
    '''\
    Represents a node of text.
    '''
    def __repr__(self):
        return 'ecoxipy.pyxom.Text(\'{}\')'.format(
            self.content.encode('unicode_escape').decode())

    def _create_sax_events(self, content_handler, indent):
        content_handler.characters(self.content)

    def _create_str(self, out):
        return out.text(self.content)

    def duplicate(self):
        return Text(self.content)


class Comment(ContentNode):
    '''\
    Represent a comment node.
    '''
    def _create_str(self, out):
        return out.comment(self.content)

    def _create_sax_events(self, content_handler, indent):
        try:
            comment = content_handler.comment
        except AttributeError:
            return
        else:
            if indent:
                indent_incr, indent_count = indent
                content_handler.characters(u'\n')
                for i in range(indent_count):
                        content_handler.characters(indent_incr)
            comment(encode(self.content))

    def __repr__(self):
        return 'ecoxipy.pyxom.Comment(\'{}\')'.format(
            self.content.encode('unicode_escape').decode())

    def duplicate(self):
        return Comment(self.content)


class ProcessingInstruction(ContentNode):
    '''\
    Represent a processing instruction.

    :param target: The processing instruction target.
    :param content: The processing instruction content or :const:`None`.
    '''
    __slots__ = ('_target')

    def __init__(self, target, content):
        ContentNode.__init__(self, content)
        self._target = target

    @staticmethod
    def create(target, content=None):
        target = _unicode(target)
        if content is not None:
            content = _unicode(content)
        return ProcessingInstruction(target, content)

    @property
    def target(self):
        return self._target

    @target.setter
    def target(self, value):
        self._target = value

    def _create_str(self, out):
        return out.processing_instruction(self._target, self.content)

    def _create_sax_events(self, content_handler, indent):
        if indent:
            indent_incr, indent_count = indent
            content_handler.characters(u'\n')
            for i in range(indent_count):
                    content_handler.characters(indent_incr)
        content_handler.processingInstruction(self.target,
            u'' if self.content is None else self.content)

    def __repr__(self):
        return 'ecoxipy.pyxom.ProcessingInstruction(\'{}\', {})'.format(
            self._target.encode('unicode_escape').decode(),
            'None' if self.content is None
            else "'{}'".format(self.content.encode(
                'unicode_escape').decode()))

    def __eq__(self, other):
        return (isinstance(other, ProcessingInstruction)
            and self._target == other._target
            and self._content == other._content)

    def __ne__(self, other):
        return (not(isinstance(other, ProcessingInstruction))
            or self._target != other._target
            or self._content != other._content)

    def duplicate(self):
        return ProcessingInstruction(self._target, self.content)


# PATH

class PyXOMPL(object):
    doctest='''\

    >>> p('html|body|_ancestor&div|attributes&"data-foo"|bar|_parent&_any|_parent&_any|p')
    >>> p('html|body^(div and where(attributes&"data-foo"|bar))|p')
    >>> p('html|body^(div and {"data-foo":bar})|p')

    >>> p('html|body|_ancestor&(div or _any|attributes&"data-foo"|bar|_parent&_any|_parent&_any)|p')
    >>> p('html|body^(div or where(attributes&"data-foo"|bar))|p')
    >>> p('html|body^(div or {"data-foo":bar})|p')

    >>> p(\'''html|body^pi()|`re.findall(r' href=".+?"', _)`|_parent&_any''\')
    >>> p(\'''html|body^(pi() and where(`re.findall(r' href=".+?"', _)`))''\')

    >>> p(\'''html|body^comment()|`_.startswith('TODO')`|_parent&_any''\')
    >>> p(\'''html|body^comment(`_.startswith('TODO')`)''\')
    >>> p(\'''html|body^(comment() and where(`_.startswith('TODO')`))''\')

    >>> p('html|body|_any|p[0]')
    >>> p('html|body|_any|div[1:4]')

    `text` := identifier | stringliteral

    `boolean_expression` := `test` (``and`` | ``or`` ) `test` | ``not`` `test`

    `python_expression` := ``\``` expression ``\```

    `test` := `text` | `boolean_expression` | `python_expression`

    `element_test` := `test` | ``element(`` [`test`] ``)``

    `text_test` := ``text(`` [`test`] ``)``

    `comment_test` := ``comment(`` [`test`] ``)``

    `pi_test` := ``pi(`` [`test`] ``)``

    `document_test` := ``document()``

    `attrs_test` := ``{`` ([`test` ``:`` `test` [``,`` `test` ``:`` `test`] ] | (`test` [``,`` `test`]*)+) ``}``

    `node_test` := `element_test` | `text_test` | `pi_test` | `comment_test` | `document_test`

    `forward_axis` := `self` | `child` | `descendant` | `attribute` | `following` | `following-sibling`

    `reverse_axis` := `parent` | `ancestor` | `preceding` | `preceding-sibling`

    `axis` := `forward_axis` | `reverse_axis`

    `step` := [`axis` ``|``] `node_test` [``[`` index | slice ``]``]

    `path` := `step` (``>`` `step`)*

    '''
    class _NodeVisitor(ast.NodeVisitor):
        def __init__(self):
            self._path = []

        def visit_Name(self, node):
            return node.id

        def visit_Str(self, node):
            return node.s

        def generic_visit(self, node):
            if isinstance(node, ast.BinOp):
                if isinstance(node.op, ast.BitOr):
                    self._path.append(self.visit(node.left))
                    self.visit(node.right)
                elif isinstance(node.op, ast.BitAnd):
                    self.visit(node.left)
                    self.visit(node.right)
                else:
                    # ast.BitXor
                    self.visit(node.left)
                    self.visit(node.right)
            else:
                ast.NodeVisitor.generic_visit(self, node)

    def __init__(self, path):
        self._steps = self._compile(path)

    @classmethod
    def _compile(self, path):
        path_ast = compile(path, '<ecoxipy.pyxom.PyXOMPL: {}>'.format(path),
            'eval',ast.PyCF_ONLY_AST)
        print(ast.dump(path_ast, False))
        visitor = self._NodeVisitor()
        visitor.visit(path_ast)
        print(visitor._path)
        '''
        print('---TRANSFORMED:---')
        print(ast.dump(path_ast, False))
        '''


del abc, collections