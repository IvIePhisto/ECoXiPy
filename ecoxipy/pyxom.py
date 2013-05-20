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

>>> from ecoxipy import MarkupBuilder
>>> b = MarkupBuilder()
>>> document = b[:'article':True] (
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
>>> document[0][1].parent is document[0]
True
>>> document[0][0] is document[0][1].previous and document[0][1].next is document[0][2]
True
>>> document.parent is None and document[0].previous is None and document[0].next is None
True

You can retrieve iterators for navigation through the tree:

>>> list(document[0][0].ancestors())
[ecoxipy.pyxom.Element('article', [...], {...}), ecoxipy.pyxom.Document('article', 'None', 'None', [...], True, 'UTF-8')]
>>> list(document[0][1].descendants())
[ecoxipy.pyxom.Text('Hello'), ecoxipy.pyxom.Element('em', [...], {...}), ecoxipy.pyxom.Text(' World'), ecoxipy.pyxom.Text('!')]
>>> list(document[0][-1].preceding_siblings())
[ecoxipy.pyxom.ProcessingInstruction('pi-target', '<PI content>'), ecoxipy.pyxom.Comment('<This is a comment!>'), ecoxipy.pyxom.Element('div', [...], {...}), ecoxipy.pyxom.Element('p', [...], {...}), ecoxipy.pyxom.Element('h1', [...], {...})]
>>> list(document[0][2][-1].preceding())
[ecoxipy.pyxom.Text('4'), ecoxipy.pyxom.Text('3'), ecoxipy.pyxom.Text('2'), ecoxipy.pyxom.Text('1'), ecoxipy.pyxom.Text('0'), ecoxipy.pyxom.Element('br', [...], {...}), ecoxipy.pyxom.Text('Some Text'), ecoxipy.pyxom.Element('p', [...], {...}), ecoxipy.pyxom.Element('data-element', [...], {...}), ecoxipy.pyxom.Element('p', [...], {...}), ecoxipy.pyxom.Element('h1', [...], {...})]
>>> list(document[0][0].following_siblings())
[ecoxipy.pyxom.Element('p', [...], {...}), ecoxipy.pyxom.Element('div', [...], {...}), ecoxipy.pyxom.Comment('<This is a comment!>'), ecoxipy.pyxom.ProcessingInstruction('pi-target', '<PI content>'), ecoxipy.pyxom.ProcessingInstruction('pi-without-content', 'None')]
>>> list(document[0][1][0].following())
[ecoxipy.pyxom.Element('em', [...], {...}), ecoxipy.pyxom.Text('!'), ecoxipy.pyxom.Element('div', [...], {...}), ecoxipy.pyxom.Comment('<This is a comment!>'), ecoxipy.pyxom.ProcessingInstruction('pi-target', '<PI content>'), ecoxipy.pyxom.ProcessingInstruction('pi-without-content', 'None')]


By supplying a test you can only nodes until a test is not satisfied. To
indicate iteration stopped because a test has failed, the last item returned
by the iterator is :const:`None` in this case.

>>> is_text = lambda context: isinstance(context, Text)
>>> list(document[0][0][0].ancestors(Element.isinstance))
[ecoxipy.pyxom.Element('h1', [...], {...}), ecoxipy.pyxom.Element('article', [...], {...}), None]
>>> list(document[0][1].descendants(Text.isinstance))
[ecoxipy.pyxom.Text('Hello'), None]
>>> list(document[0][-1].preceding_siblings(ProcessingInstruction.isinstance))
[ecoxipy.pyxom.ProcessingInstruction('pi-target', '<PI content>'), None]
>>> list(document[0][2][-6].preceding(Element.isinstance))
[ecoxipy.pyxom.Element('br', [...], {...}), None]
>>> list(document[0][0].following_siblings(Element.isinstance))
[ecoxipy.pyxom.Element('p', [...], {...}), ecoxipy.pyxom.Element('div', [...], {...}), None]
>>> list(document[0][1][0].following(Element.isinstance))
[ecoxipy.pyxom.Element('em', [...], {...}), None]


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

from ecoxipy import _python3, _unicode
import ecoxipy.string_output


class XMLNode(object):
    '''\
    Base class for XML node objects.

    Retrieving the byte string from an instance yields a byte string encoded
    as `UTF-8`.
    '''
    __metaclass__ = abc.ABCMeta
    __slots__ = ('_parent', '_next', '_previous')

    @property
    def parent(self):
        '''\
        The parent :class:`ContainerNode` or :const:`None` if the node has no
        parent.
        '''
        try:
            return self._parent
        except AttributeError:
            return None

    def _attribute_iterator(self, attribute, test):
        if test is None:
            test = lambda context: True
        def iterator(current):
            while True:
                current = getattr(current, attribute)
                if current is None:
                    break
                elif not test(current):
                    yield None
                    break
                else:
                    yield current
        return iterator(self)

    def _attribute_parent_iterator(self, attribute, test):
        siblings = getattr(self, attribute + '_siblings')(test)
        go_up = True
        for sibling in siblings:
            if sibling is None:
                go_up = False
            yield sibling
        if go_up:
            parent = self.parent
            if parent is not None:
                for parent_sibling in getattr(parent, attribute)(test):
                    yield parent_sibling

    def ancestors(self, test=None):
        '''\
        Returns an iterator over all ancestors satisfying a test.

        :param test: A callable to execute for each ancestor. If the return
            value evaluates to a boolean :const:`True` the ancestor will be
            returned by the iterator, otherwise it won't and no more ancestors
            are returned. If ``test`` is :const:`None` every ancestor will
            be returned.
        :returns: An iterator over the ancestors satisfying the test.
        '''
        return self._attribute_iterator('parent', test)

    @property
    def previous(self):
        '''\
        The previous :class:`XMLNode` or :const:`None` if the node has no
        preceding sibling.
        '''
        try:
            return self._previous
        except AttributeError:
            return None

    def preceding_siblings(self, test=None):
        '''\
        Returns an iterator over all preceding siblings satisfying a test.

        :param test: A callable to execute for each previous sibling. If the
            return value evaluates to a boolean :const:`True` the sibling
            will be returned by the iterator, otherwise it won't and no more
            siblings are returned. If ``test`` is :const:`None` every
            sibling will be returned.
        :returns: An iterator over the preceding siblings satisfying the test.
        '''
        return self._attribute_iterator('previous', test)

    def preceding(self, test=None):
        '''\
        Returns an iterator over all preceding nodes satisfying a test.

        :param test: A callable to execute for each preceding node. If the
            return value evaluates to a boolean :const:`True` the sibling
            will be returned by the iterator, otherwise it won't and no more
            preceding nodes are returned. If ``test`` is :const:`None` every
            preceding node will be returned.
        :returns: An iterator over the preceding nodes satisfying the test.
        '''
        return self._attribute_parent_iterator('preceding', test)

    @property
    def next(self):
        '''\
        The next :class:`XMLNode` or :const:`None` if the node has no
        following sibling.
        '''
        try:
            return self._next
        except AttributeError:
            return None

    def following_siblings(self, test=None):
        '''\
        Returns an iterator over all following siblings satisfying a test.

        :param test: A callable to execute for each following sibling. If the
            return value evaluates to a boolean :const:`True` the sibling
            will be returned by the iterator, otherwise it won't and no more
            siblings are returned. If ``test`` is :const:`None` every
            sibling will be returned.
        :returns: An iterator over the following siblings satisfying the test.
        '''
        return self._attribute_iterator('next', test)

    def following(self, test=None):
        '''\
        Returns an iterator over all following nodes satisfying a test.

        :param test: A callable to execute for each following node. If the
            return value evaluates to a boolean :const:`True` the sibling
            will be returned by the iterator, otherwise it won't and no more
            following nodes are returned. If ``test`` is :const:`None` every
            following node will be returned.
        :returns: An iterator over the following nodes satisfying the test.
        '''
        return self._attribute_parent_iterator('following', test)

    def __str__(self):
        '''\
        Creates a Unicode string containing the XML representation of
        the node.
        '''
        return self.create_str(encoding=None)

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

    @abc.abstractmethod
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

    @abc.abstractmethod
    def _create_sax_events(self, content_handler, indent):
        pass

    @abc.abstractmethod
    def __repr__(self):
        pass

    @classmethod
    def isinstance(cls, content):
        return isinstance(content, cls)


class ContainerNode(XMLNode, collections.MutableSequence):
    __metaclass__ = abc.ABCMeta
    __slots__ = ('_children')

    def __init__(self, children):
        self._children = children
        for i, child in enumerate(children):
            child._parent = self
            if i > 0:
                self._wire_neighbors(previous, child)
            previous = child

    def __getitem__(self, index):
        return self._children[index]

    def _unwire_child(self, child):
        del child._parent
        del child._next
        del child._previous

    def _wire_neighbors(self, left, right):
        left._next = right
        right._previous = left

    def _wire_child(self, index, child):
        child._parent = self
        if len(self) > 1:
            if index > 0:
                self._wire_neighbors(self[index-1], child)
            if index < len(self) - 1:
                self._wire_neighbors(child, self[index+1])

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

    def __len__(self):
        return len(self._children)

    def __iter__(self):
        return self._children.__iter__()

    def __contains__(self, item):
        return item in self._children

    def __call__(self, *path):
        return Finder.find(self, path)

    def descendants(self, test=None):
        '''\
        Returns an iterator over all descendants satisfying a test.

        :param test: A callable to execute for each descendant. If the return
            value evaluates to a boolean :const:`True` the descendant will be
            returned by the iterator, otherwise it won't and neither its
            children. If ``test`` is :const:`None` every descendant will be
            returned.
        :returns: An iterator over the descendants satisfying the test.
        '''
        if test is None:
            test = lambda context: True
        def iterator():
            for child in self:
                if test(child):
                    yield child
                    if isinstance(child, ContainerNode):
                        for descendant in child.descendants(test):
                            yield descendant
                else:
                    yield None
                    break
        return iterator()


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

    def __bytes__(self):
        '''\
        Creates a byte string containing the XML representation of the
        node with the encoding :meth:`encoding`.
        '''
        return self.create_str(encoding=self._encoding)

    if not _python3:
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
        return 'ecoxipy.pyxom.Document(\'{}\', \'{}\', \'{}\', [...], {}, \'{}\')'.format(
            self._doctype.name.encode('unicode_escape').decode(),
            _unicode(self._doctype.publicid).encode('unicode_escape').decode(),
            _unicode(self._doctype.systemid).encode('unicode_escape').decode(),
            repr(self._omit_xml_declaration),
            self._encoding.encode('unicode_escape').decode())


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
        self._attributes = attributes

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


class Text(XMLNode):
    __slots__ = ('_value', '_parent')

    def __init__(self, value):
        self._value = value

    @property
    def value(self):
        return self._value

    def __repr__(self):
        return 'ecoxipy.pyxom.Text(\'{}\')'.format(
            self._value.encode('unicode_escape').decode())

    def _create_sax_events(self, content_handler, indent):
        content_handler.characters(self._value)

    def _create_str(self, out):
        return out.text(self._value)


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
                content_handler.characters(u'\n')
                for i in range(indent_count):
                        content_handler.characters(indent_incr)
            comment(encode(self._content))

    def __repr__(self):
        return 'ecoxipy.pyxom.Comment(\'{}\')'.format(
            self._content.encode('unicode_escape').decode())


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
            content_handler.characters(u'\n')
            for i in range(indent_count):
                    content_handler.characters(indent_incr)
        content_handler.processingInstruction(self.target,
            u'' if self._content is None else self._content)

    def __repr__(self):
        return 'ecoxipy.pyxom.ProcessingInstruction(\'{}\', \'{}\')'.format(
            self._target.encode('unicode_escape').decode(),
            'None' if self._content is None
            else self._content.encode('unicode_escape').decode())


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