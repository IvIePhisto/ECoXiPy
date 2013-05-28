# -*- coding: utf-8 -*-
u'''\
PyXOM - Pythonic XML Object Model
=================================

This module implements a pythonic object model for the representation of XML
structures. To create PyXOM data conveniently use :mod:`ecoxipy.pyxom.output`.

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
...             'Hello', Element.create('em', ' World',
...                 attributes={'count':1}), '!'
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
...         b['foo:somexml'](
...             b['foo:somexml']({'foo:bar': 1, 't:test': 2}),
...             b['somexml']({'xmlns': ''}),
...             b['bar:somexml'],
...             {'xmlns:foo': 'foo://bar', 'xmlns:t': '',
...                 'foo:bar': 'Hello'}
...         ),
...         {'xmlns': 'http://www.w3.org/1999/xhtml/'}
...     ), doctype_name='article', omit_xml_declaration=True
... )


Enforcing Well-Formedness
^^^^^^^^^^^^^^^^^^^^^^^^^

Using the :meth:`create` methods or supplying the parameter
``check_well_formedness`` as :const:`True` to the appropriate constructors
enforces that the element, attribute and document type names are valid XML
names, and that processing instruction target and content as well as comment
contents conform to their constraints:

>>> from ecoxipy import XMLWellFormednessException
>>> def catch_not_well_formed(cls, *args, **kargs):
...     try:
...         return cls.create(*args, **kargs)
...     except XMLWellFormednessException as e:
...         print(e)
>>> t = catch_not_well_formed(Document, [], doctype_name='1nvalid-xml-name')
The value "1nvalid-xml-name" is not a valid XML name.
>>> t = catch_not_well_formed(Document, [], doctype_name='html', doctype_publicid='"')
The value "\\"" is not a valid document type public ID.
>>> t = catch_not_well_formed(Document, [], doctype_name='html', doctype_systemid='"\\'')
The value "\\"'" is not a valid document type system ID.
>>> t = catch_not_well_formed(Element, '1nvalid-xml-name', [], {})
The value "1nvalid-xml-name" is not a valid XML name.
>>> t = catch_not_well_formed(Element, 't', [], attributes={'1nvalid-xml-name': 'content'})
The value "1nvalid-xml-name" is not a valid XML name.
>>> t = catch_not_well_formed(ProcessingInstruction, '1nvalid-xml-name')
The value "1nvalid-xml-name" is not a valid XML processing instruction target.
>>> t = catch_not_well_formed(ProcessingInstruction, 'target', 'invalid PI content ?>')
The value "invalid PI content ?>" is not a valid XML processing instruction content because it contains "?>".
>>> t = catch_not_well_formed(Comment, 'invalid XML comment --')
The value "invalid XML comment --" is not a valid XML comment because it contains "--".


Navigation
^^^^^^^^^^

Use list semantics to retrieve child nodes and attribute access to retrieve
node information:

>>> print(document.doctype.name)
article
>>> print(document[0].name)
article
>>> print(document[0].attributes['xmlns'].value)
http://www.w3.org/1999/xhtml/
>>> print(document[0][-3].target)
pi-target
>>> document[0][1].parent is document[0]
True
>>> document[0][0] is document[0][1].previous and document[0][1].next is document[0][2]
True
>>> document.parent is None and document[0].previous is None and document[0].next is None
True
>>> document[0].attributes.parent is document[0]
True


You can retrieve iterators for navigation through the tree:

>>> list(document[0][0].ancestors)
[ecoxipy.pyxom.Element['article', {...}], ecoxipy.pyxom.Document[ecoxipy.pyxom.DocumentType('article', None, None), True, 'UTF-8']]
>>> list(document[0][1].children())
[ecoxipy.pyxom.Text('Hello'), ecoxipy.pyxom.Element['em', {...}], ecoxipy.pyxom.Text('!')]
>>> list(document[0][1].children(True))
[ecoxipy.pyxom.Text('!'), ecoxipy.pyxom.Element['em', {...}], ecoxipy.pyxom.Text('Hello')]
>>> list(document[0][1].descendants())
[ecoxipy.pyxom.Text('Hello'), ecoxipy.pyxom.Element['em', {...}], ecoxipy.pyxom.Text(' World'), ecoxipy.pyxom.Text('!')]
>>> list(document[0][1].descendants(True))
[ecoxipy.pyxom.Text('!'), ecoxipy.pyxom.Element['em', {...}], ecoxipy.pyxom.Text(' World'), ecoxipy.pyxom.Text('Hello')]
>>> list(document[0][-2].preceding_siblings)
[ecoxipy.pyxom.ProcessingInstruction('pi-target', '<PI content>'), ecoxipy.pyxom.Comment('<This is a comment!>'), ecoxipy.pyxom.Element['div', {...}], ecoxipy.pyxom.Element['p', {...}], ecoxipy.pyxom.Element['h1', {...}]]
>>> list(document[0][2][-1].preceding)
[ecoxipy.pyxom.Text('4'), ecoxipy.pyxom.Text('3'), ecoxipy.pyxom.Text('2'), ecoxipy.pyxom.Text('1'), ecoxipy.pyxom.Text('0'), ecoxipy.pyxom.Element['br', {...}], ecoxipy.pyxom.Text('Some Text'), ecoxipy.pyxom.Element['p', {...}], ecoxipy.pyxom.Element['data-element', {...}], ecoxipy.pyxom.Element['p', {...}], ecoxipy.pyxom.Element['h1', {...}]]
>>> list(document[0][0].following_siblings)
[ecoxipy.pyxom.Element['p', {...}], ecoxipy.pyxom.Element['div', {...}], ecoxipy.pyxom.Comment('<This is a comment!>'), ecoxipy.pyxom.ProcessingInstruction('pi-target', '<PI content>'), ecoxipy.pyxom.ProcessingInstruction('pi-without-content', None), ecoxipy.pyxom.Element['foo:somexml', {...}]]
>>> list(document[0][1][0].following)
[ecoxipy.pyxom.Element['em', {...}], ecoxipy.pyxom.Text('!'), ecoxipy.pyxom.Element['div', {...}], ecoxipy.pyxom.Comment('<This is a comment!>'), ecoxipy.pyxom.ProcessingInstruction('pi-target', '<PI content>'), ecoxipy.pyxom.ProcessingInstruction('pi-without-content', None), ecoxipy.pyxom.Element['foo:somexml', {...}]]


Namespaces
""""""""""

PyXOM supports the interpretation of `Namespaces in XML
<http://www.w3.org/TR/REC-xml-names/`_. Namespace prefix and local names are
calculated from :class:`Element` and :class:`Attribute` names:

>>> document[0].namespace_prefix == None
True
>>> print(document[0].local_name)
article
>>> print(document[0][-1].namespace_prefix)
foo
>>> print(document[0][-1].local_name)
somexml
>>> attr = document[0][-1].attributes['foo:bar']
>>> print(attr.namespace_prefix)
foo
>>> print(attr.local_name)
bar


The namespace URI is available as :attr:`Element.namespace_uri` and
:attr:`Attribute.namespace_uri`, these properties look up the namespace
prefix of the node in the parent elements:

>>> xhtml_namespace_uri = u'http://www.w3.org/1999/xhtml/'
>>> document[0][1].namespace_uri == xhtml_namespace_uri
True
>>> document[0][1][1].namespace_uri == xhtml_namespace_uri
True
>>> document[0][-1][0].namespace_uri == u'foo://bar'
True
>>> document[0][-1][0].attributes['foo:bar'].namespace_uri == u'foo://bar'
True


The namespace prefixes active on an element are available as the iterator
:attr:`Element.namespace_prefixes`:

>>> prefixes = sorted(list(document[0][-1][0].namespace_prefixes),
...     key=lambda value: '' if value is None else value)
>>> prefixes[0] == None
True
>>> print(u', '.join(prefixes[1:]))
foo, t
>>> document[0][-1][0].get_namespace_uri(u'foo') == u'foo://bar'
True
>>> print(list(document[0].namespace_prefixes))
[None]
>>> document[0].get_namespace_uri(None) == u'http://www.w3.org/1999/xhtml/'
True

If an element or attribute is in no namespace, ``namespace_uri`` is
:const:`None`:

>>> document[0][-1][0].attributes['t:test'].namespace_uri == None
True
>>> document[0][-1][1].namespace_uri == None
True


If an undefined namespace prefix is used, the ``namespace_uri`` is
:const:`False`:

>>> document[0][-1][2].namespace_uri == False
True


Manipulation and Equality
^^^^^^^^^^^^^^^^^^^^^^^^^

All :class:`XMLNode` instances have attributes which allow for modification.
:class:`Document` and :class:`Element` instances also allow modification of
their contents like sequences.


Duplication and Comparisons
"""""""""""""""""""""""""""

Use :meth:`duplicate` to create a deep copy of a XML node:

>>> document_copy = document.duplicate()
>>> document is document_copy
False


Equality and inequality recursively compare XML nodes:

>>> document == document_copy
True
>>> document != document_copy
False


Attributes
""""""""""

Attributes are :class:`Attribute` instances are contained in one
:class:`Attributes` instance per :class:`Element`:

>>> document_copy[0][0].attributes['data']
ecoxipy.pyxom.Attribute('data', 'to quote: <&>"\\'')
>>> old_data = document_copy[0][0].attributes['data'].value
>>> document_copy[0][0].attributes['data'].value = 'foo bar'
>>> document_copy[0][0].attributes['data'].value == u'foo bar'
True
>>> 'data' in document_copy[0][0].attributes
True
>>> document == document_copy
False
>>> document != document_copy
True
>>> document_copy[0][0].attributes.create_attribute('foo', 'bar')
>>> foo_attr = document_copy[0][0].attributes['foo']
>>> 'foo' in document_copy[0][0].attributes
True
>>> document_copy[0][0].attributes.remove(foo_attr)
>>> 'foo' in document_copy[0][0].attributes
False
>>> foo_attr.parent == None
True
>>> document_copy[0][0].attributes.add(foo_attr)
>>> 'foo' in document_copy[0][0].attributes
True
>>> foo_attr.parent == document_copy[0][0].attributes
True
>>> foo_attr.parent != document_copy[0][0].attributes
False
>>> del document_copy[0][0].attributes['foo']
>>> 'foo' in document_copy[0][0].attributes
False
>>> document_copy[0][0].attributes['data'].value = old_data
>>> document == document_copy
True
>>> document != document_copy
False
>>> attr = document[0][-1].attributes['foo:bar']
>>> attr.name = 'test'
>>> attr.namespace_prefix is None
True
>>> print(attr.local_name)
test


Other Nodes
"""""""""""

>>> document_copy[0].insert(1, document_copy[0][0])
>>> document_copy[0][0] == document[0][1]
True
>>> document_copy[0][0] != document[0][1]
False
>>> document_copy[0][1] == document[0][0]
True
>>> document_copy[0][1] != document[0][0]
False
>>> p_element = document_copy[0][0]
>>> document_copy[0].remove(p_element)
>>> document_copy[0][0].name == u'h1' and p_element.parent is None
True
>>> document_copy[0][0].append(p_element)
>>> document_copy[0][0][-1] is p_element
True
>>> p_element in document_copy[0][0]
True
>>> p_element in document[0]
False
>>> document[0][1] in document_copy[0][0]
False
>>> document[0][1] is document_copy[0][0][-1]
False
>>> document[0][1] == document_copy[0][0][-1]
True
>>> document[0][1] != document_copy[0][0][-1]
False
>>> document[0][-1].name = 'foo'
>>> document[0][-1].namespace_prefix is None
True
>>> print(document[0][-1].local_name)
foo


XML Serialization
^^^^^^^^^^^^^^^^^

First we remove embedded non-HTML XML, as there are multiple attributes on the
element and the order they are rendered in is indeterministic, which makes it
hard to compare:

>>> del document[0][-1]


Getting the Unicode value of an document yields the XML document serialized as
an Unicode string:

>>> document_string = u"""<!DOCTYPE article><article xmlns="http://www.w3.org/1999/xhtml/"><h1 data="to quote: &lt;&amp;&gt;&quot;'">&lt;Example&gt;</h1><p umlaut-attribute="äöüß">Hello<em count="1"> World</em>!</p><div><data-element>äöüß &lt;&amp;&gt;</data-element><p attr="value">raw content</p>Some Text<br/>012345</div><!--<This is a comment!>--><?pi-target <PI content>?><?pi-without-content?></article>"""
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

>>> document_string = u"""<?xml version="1.0" encoding="UTF-8"?>\\n<article xmlns="http://www.w3.org/1999/xhtml/"><h1 data="to quote: &lt;&amp;&gt;&quot;'">&lt;Example&gt;</h1><p umlaut-attribute="äöüß">Hello<em count="1"> World</em>!</p><div><data-element>äöüß &lt;&amp;&gt;</data-element><p attr="value">raw content</p>Some Text<br></br>012345</div><?pi-target <PI content>?><?pi-without-content ?></article>"""
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
... <article xmlns="http://www.w3.org/1999/xhtml/">
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
import collections
from xml.sax.xmlreader import AttributesImpl
from xml.sax.saxutils import XMLGenerator

from ecoxipy import _python2, _unicode
from ecoxipy.string_output import StringOutput
from ecoxipy import _helpers


class XMLNode(object):
    '''\
    Base class for XML node objects.

    Retrieving the byte string from an instance yields a byte string encoded
    as `UTF-8`.
    '''
    __metaclass__ = abc.ABCMeta
    __slots__ = ('_parent', '_next', '_previous')

    _string_output = StringOutput()

    def _attribute_node(self, attribute):
        try:
            return getattr(self, attribute)
        except AttributeError:
            return None

    @property
    def parent(self):
        '''\
        The parent :class:`ContainerNode` or :const:`None` if the node has no
        parent.
        '''
        return self._attribute_node('_parent')

    @property
    def previous(self):
        '''\
        The previous :class:`XMLNode` or :const:`None` if the node has no
        preceding sibling.
        '''
        return self._attribute_node('_previous')

    @property
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

    @property
    def ancestors(self):
        '''\
        Returns an iterator over all ancestors.
        '''
        return self._attribute_iterator('_parent')

    @property
    def preceding_siblings(self):
        '''\
        Returns an iterator over all preceding siblings.
        '''
        return self._attribute_iterator('_previous')

    @property
    def following_siblings(self):
        '''\
        Returns an iterator over all following siblings.
        '''
        return self._attribute_iterator('_next')

    def _attribute_climbing_iterator(self, attribute):
        siblings = self._attribute_iterator(attribute)
        for sibling in siblings:
            yield sibling
        parent = self.parent
        if parent is not None:
            for parent_sibling in parent._attribute_climbing_iterator(
                    attribute):
                yield parent_sibling

    @property
    def preceding(self):
        '''\
        Returns an iterator over all preceding nodes.
        '''
        return self._attribute_climbing_iterator('_previous')

    @property
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
            out = self._string_output
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
            content_handler = XMLGenerator(out, out_encoding)
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
    __slots__ = ('_children')

    def __init__(self, children):
        self._children = children
        for i, child in enumerate(children):
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
        try:
            child._clear_namespace_uri()
        except AttributeError:
            pass
        try:
            del child._parent
        except AttributeError:
            pass
        self._wire_neighbors(child.previous, child.next)
        try:
            del child._next
        except AttributeError:
            pass
        try:
            del child._previous
        except AttributeError:
            pass

    def _wire_neighbors(self, left, right):
        if left is not None:
            left._next = right
        if right is not None:
            right._previous = left

    def _remove_from_parent(self, child):
        old_parent = child.parent
        if old_parent is not None:
            old_parent.remove(child)

    def _wire_child(self, index, child):
        child._parent = self
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
        for current_child in self._children:
            if child is current_child:
                return True
        return False

    def __reversed__(self):
        return self._children.__reversed__()

    def __setitem__(self, index, child):
        self._remove_from_parent(child)
        try:
            old_child = self._children[index]
        except IndexError:
            old_child = None
        self._children[index] = child
        if old_child is not None:
            self._unwire_child(old_child)
        self._wire_child(index, child)

    def insert(self, index, child):
        self._remove_from_parent(child)
        self._children.insert(index, child)
        self._wire_child(index, child)

    def __delitem__(self, index):
        child = self._children[index]
        del self._children[index]
        self._unwire_child(child)

    def remove(self, child):
        for index, current_child in enumerate(self._children):
            if child is current_child:
                del self[index]
                return
        raise ValueError(child)


_string_repr = lambda value: 'None' if value is None else "'{}'".format(
    value.encode('unicode_escape').decode().replace("'", "\\'"))


class DocumentType(object):
    '''\
    Represents a document type declaration of a :class:`Document`. It should
    not be instantiated on itself.

    :param name: The document element name.
    :type name: Unicode string
    :param publicid: The document type public ID or :const:`None`.
    :type publicid: Unicode string
    :param systemid: The document type system ID or :const:`None`.
    :type systemid: Unicode string
    :param check_well_formedness: If :const:`True` the document element name
        will be checked to be a valid XML name.
    :type check_well_formedness: :func:`bool`
    '''
    __slots__ = ('_name', '_publicid', '_systemid', '_check_well_formedness')

    def __init__(self, name, publicid, systemid, check_well_formedness):
        if check_well_formedness:
            if name is not None:
                _helpers.enforce_valid_xml_name(name)
            if publicid is not None:
                _helpers.enforce_valid_doctype_publicid(publicid)
            if systemid is not None:
                _helpers.enforce_valid_doctype_systemid(systemid)
        self._name = name
        self._publicid = publicid
        self._systemid = systemid
        self._check_well_formedness = check_well_formedness

    @property
    def name(self):
        '''\
        The document element name.
        '''
        return self._name

    @name.setter
    def name(self, name):
        if name is None:
            self._publicid = None
            self._systemid = None
        else:
            name = _unicode(name)
            if self._check_well_formedness:
                _helpers.enforce_valid_xml_name(name)
        self._name = name

    @property
    def publicid(self):
        '''\
        The document type public ID or :const:`None`
        '''
        return self._publicid

    @publicid.setter
    def publicid(self, publicid):
        if publicid is not None:
            publicid = _unicode(publicid)
            if self._check_well_formedness:
                _helpers.enforce_valid_doctype_publicid(publicid)
        self._publicid = publicid

    @property
    def systemid(self):
        '''\
        The document type system ID or :const:`None`
        '''
        return self._systemid

    @systemid.setter
    def systemid(self, systemid):
        if systemid is not None:
            systemid = _unicode(systemid)
            if self._check_well_formedness:
                _helpers.enforce_valid_doctype_systemid(systemid)
        self._systemid = systemid

    def __repr__(self):
        return 'ecoxipy.pyxom.DocumentType({}, {}, {})'.format(
            _string_repr(self._name),
            _string_repr(self._publicid),
            _string_repr(self._systemid),
        )

    def __eq__(self, other):
        return (isinstance(other, DocumentType)
            and self._name == other._name
            and self._publicid == other._publicid
            and self._systemid == other._systemid
        )

    def __ne__(self, other):
        return (not(isinstance(other, DocumentType))
            or self._name != other._name
            or self._publicid != other._publicid
            or self._systemid != other._systemid
        )


class Document(ContainerNode):
    '''\
    Represents a XML document.

    :param doctype_name: The document type root element name or :const:`None`
        if the document should not have document type declaration.
    :type doctype_name: Unicode string
    :param doctype_publicid: The public ID of the document type declaration
        or :const:`None`.
    :type doctype_publicid: Unicode string
    :param doctype_systemid: The system ID of the document type declaration
        or :const:`None`.
    :type doctype_systemid: Unicode string
    :param children: The document root :class:`XMLNode` instances.
    :param encoding: The encoding of the document. If it is :const:`None`
        `UTF-8` is used.
    :type encoding: Unicode string
    :param omit_xml_declaration: If :const:`True` the XML declaration is
        omitted.
    :type omit_xml_declaration: :func:`bool`
    :param check_well_formedness: If :const:`True` the document element name
        will be checked to be a valid XML name.
    :type check_well_formedness: :func:`bool`
    :raises ecoxipy.XMLWellFormednessException: If ``check_well_formedness``
        is :const:`True` and ``doctype_name`` is not a valid XML name,
        ``doctype_publicid`` is not a valid public ID or ``doctype_systemid``
        is not a valid system ID.
    '''
    __slots__ = ('_doctype', '_omit_xml_declaration', '_encoding')

    def __init__(self, doctype_name, doctype_publicid, doctype_systemid,
            children, omit_xml_declaration, encoding,
            check_well_formedness=False):
        ContainerNode.__init__(self, children)
        self._doctype = DocumentType(doctype_name, doctype_publicid,
            doctype_systemid, check_well_formedness)
        self._omit_xml_declaration = omit_xml_declaration
        if encoding is None:
            encoding = u'UTF-8'
        self._encoding = encoding

    @staticmethod
    def create(*children, **kargs):
        '''\
        Creates a document and converts parameters to appropriate types.

        :param children: The document root nodes. All items that are not
            :class:`XMLNode` instances create :class:`Text` nodes after they
            have been converted to Unicode strings.
        :param kargs: The parameters as the constructor has (except
            ``children``) are recognized. The items ``doctype_name``,
            ``doctype_publicid``, ``doctype_systemid``, and ``encoding`` are
            converted to Unicode strings if they are not :const:`None`.
            ``omit_xml_declaration`` is converted to boolean.
        :returns: The created document.
        :rtype: :class:`Document`
        :raises ecoxipy.XMLWellFormednessException: If ``doctype_name`` is not
            a valid XML name, ``doctype_publicid`` is not a valid public ID or
            ``doctype_systemid`` is not a valid system ID.
        '''
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
            ], omit_xml_declaration, encoding, True)

    @property
    def doctype(self):
        '''\
        The :class:`DocumentType` instance of the document or :const:`None`.
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
        self._omit_xml_declaration = bool(value)

    @property
    def encoding(self):
        '''\
        The encoding of the document.
        '''
        return self._encoding

    @encoding.setter
    def encoding(self, value):
        if value is not None:
            value = _unicode(value)
        else:
            value = u'UTF-8'
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
        return 'ecoxipy.pyxom.Document[{}, {}, {}]'.format(
            repr(self._doctype),
            repr(self._omit_xml_declaration),
            _string_repr(self._encoding))

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
                or self._encoding != other._encoding
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


class NamespaceNameMixin(object):
    __metaclass__ = abc.ABCMeta
    _namespace_name_slots__ = ('_namespace_prefix', '_local_name',
        '_v_namespace_uri', '_v_namespace_source')

    def _set_namespace_properties(self, index):
        components = _helpers.get_qualified_name_components(self.name)
        self._namespace_prefix, self._local_name = components
        return components[index]

    def _clear_namespace_uri(self):
        try:
            del self._v_namespace_uri
        except AttributeError:
            pass
        else:
            self._v_namespace_source._remove_namespace_target(self)
            del self._v_namespace_source

    def _clear_namespace_properties(self):
        del self._namespace_prefix
        del self._local_name
        self._clear_namespace_uri()

    @property
    def namespace_prefix(self):
        try:
            return self._namespace_prefix
        except AttributeError:
            return self._set_namespace_properties(0)

    @property
    def local_name(self):
        try:
            return self._local_name
        except AttributeError:
            return self._set_namespace_properties(1)

    @property
    def namespace_uri(self):
        try:
            return self._v_namespace_uri
        except AttributeError:
            if isinstance(self, Attribute):
                namespace_source = self.parent.parent
            else:
                namespace_source = self
            namespace_source, namespace_uri = namespace_source._get_namespace(
                self.namespace_prefix)
            if namespace_source is not None:
                namespace_source._register_namespace_target(self)
            self._v_namespace_source = namespace_source
            self._v_namespace_uri = namespace_uri
            return namespace_uri


class Attribute(NamespaceNameMixin):
    __slots__ = NamespaceNameMixin._namespace_name_slots__ + (
        '_parent', '_name', '_value', '_check_well_formedness',
        '_namespace_attribute_prefix')

    def __init__(self, parent, name, value, check_well_formedness):
        if check_well_formedness:
            _helpers.enforce_valid_xml_name(name)
        self._parent = parent
        self._namespace_attribute_prefix = False
        self._name = name
        self._value = value
        self._check_well_formedness = check_well_formedness
        self._update_namespace_prefix()

    def _set_namespace(self, prefix, value):
        attributes = self.parent
        if len(value) == 0:
            value = None
        if attributes is not None:
            attributes.parent._set_namespace(prefix, value)

    def _remove_namespace(self, prefix):
        attributes = self.parent
        if attributes is not None:
            attributes.parent._remove_namespace(prefix)

    def _update_namespace_uri(self):
        prefix = self._namespace_attribute_prefix
        if prefix is not False:
            self._set_namespace(prefix, self._value)

    def _update_namespace_prefix(self):
        name = self._name
        if name == u'xmlns':
            prefix = None
        elif name.startswith(u'xmlns:') and len(name) > 6:
            prefix = name[6:]
        else:
            prefix = False
        old_prefix = self._namespace_attribute_prefix
        if prefix != old_prefix:
            if old_prefix is not False:
                self._remove_namespace(old_prefix)
            if prefix is not False:
                self._set_namespace(prefix, self._value)
            self._namespace_attribute_prefix = prefix

    @property
    def parent(self):
        '''\
        The parent :class:`Attributes`.
        '''
        try:
            return self._parent
        except AttributeError:
            return None

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        name = _unicode(name)
        if name == self._name:
            return
        if self._check_well_formedness:
            _helpers.enforce_valid_xml_name(name)
        if name in self._parent._attributes:
            raise KeyError(
                u'An attribute with name "{}" does already exist in the parent.'.format(
                    name))
        del self._parent._attributes[self._name]
        self._parent._attributes[name] = self
        self._name = name
        self._clear_namespace_properties()
        self._update_namespace_prefix()

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        value = _unicode(value)
        if value == self._value:
            return
        self._update_namespace_uri()
        self._value = value

    def __repr__(self):
        return 'ecoxipy.pyxom.Attribute({}, {})'.format(
            _string_repr(self._name), _string_repr(self._value))

    def __eq__(self, other):
        return (isinstance(other, Attribute)
            and self.name == other.name
            and self.value == other.value)

    def __ne__(self, other):
        return (not(isinstance(other, Attribute))
            or self.name != other.name
            or self.value != other.value)


class Attributes(collections.Mapping):
    '''\
    Represents the attributes of an :class:`Element`. It should not be
    instantiated on itself.
    '''
    __slots__ = ('_parent', '_attributes', '_check_well_formedness')

    def __init__(self, parent, attributes, check_well_formedness):
        self._parent = parent
        self._attributes = {}
        for name in attributes:
            value = attributes[name]
            self._attributes[name] = Attribute(self, name, value,
                check_well_formedness)
        self._check_well_formedness = check_well_formedness

    def __len__(self):
        return len(self._attributes)

    def __iter__(self):
        return self._attributes.__iter__()

    def __contains__(self, name):
        name = _unicode(name)
        return name in self._attributes

    def __getitem__(self, name):
        name = _unicode(name)
        return self._attributes[name]

    def __delitem__(self, name):
        name = _unicode(name)
        item = self._attributes[name]
        item._clear_namespace_uri()
        del self._attributes[name]
        del item._parent

    def create_attribute(self, name, value):
        name = _unicode(name)
        if name in self._attributes:
            raise KeyError(
                u'An attribute with name "{}" already exists.'.format(name))
        value = _unicode(value)
        self._attributes[name] = Attribute(self, name, value,
            self._check_well_formedness)

    def add(self, attribute):
        if not isinstance(attribute, Attribute):
            raise ValueError(
                'The parameter "attribute" must be an "ecoxipy.pyxom.Attribute" instance.')
        if attribute.name in self._attributes:
            raise KeyError(
                u'An attribute with name "{}" already exists.'.format(name))
        parent = attribute.parent
        attribute._clear_namespace_uri()
        if parent is not None:
            parent.remove(attribute)
        self._attributes[attribute.name] = attribute
        attribute._parent = self

    def remove(self, attribute):
        self_attribute = self._attributes[attribute.name]
        if self_attribute is not attribute:
            raise ValueError(
                'The parameter "attribute" must be contained within object.')
        del self[attribute.name]

    @property
    def parent(self):
        '''\
        The parent :class:`Element`.
        '''
        return self._parent

    def __repr__(self):
        return 'ecoxipy.pyxom.Attributes{}'.format(
            ', '.join([repr(attribute) for attribute in self.values()]))

    def to_dict(self):
        return {
            attribute.name: attribute.value
            for attribute in self.values()
        }


class Element(ContainerNode, NamespaceNameMixin):
    '''\
    Represents a XML element.

    :param name: The name of the element to create.
    :type name: Unicode string
    :param children: The children :class:`XMLNode` instances of the element.
    :type children: iterable of items
    :param attributes: Defines the attributes of the element. Must be usable
        as the parameter of :func:`dict` and should contain only Unicode
        strings as key and value definitions.
    :param check_well_formedness: If :const:`True` the element name and
        attribute names will be checked to be a valid XML name.
    :type check_well_formedness: :func:`bool`
    :raises ecoxipy.XMLWellFormednessException: If
        ``check_well_formedness`` is :const:`True` and the
        ``name`` is not a valid XML name.
    '''
    __slots__ = NamespaceNameMixin._namespace_name_slots__ + (
        '_name', '_attributes', '_check_well_formedness',
        '_namespace_prefix_to_uri', '_namespace_targets',
        '_namespace_prefix_to_target')

    def __init__(self, name, children, attributes,
            check_well_formedness=False):
        if check_well_formedness:
            _helpers.enforce_valid_xml_name(name)
        ContainerNode.__init__(self, children)
        self._name = name
        self._namespace_prefix_to_uri = {}
        self._namespace_targets = {}
        self._namespace_prefix_to_target = {}
        self._attributes = Attributes(self, attributes, check_well_formedness)
        self._check_well_formedness = check_well_formedness

    @staticmethod
    def create(name, *children, **kargs):
        '''\
        Creates an element and converts parameters to appropriate types.

        :param children: The element child nodes. All items that are not
            :class:`XMLNode` instances create :class:`Text` nodes after they
            have been converted to Unicode strings.
        :param kargs: The item ``attributes`` defines the attributes and must
            have a method :meth:`items()` (like :func:`dict`) which returns
            an iterable of 2-:func:`tuple` instances containing the attribute
            name as the first and the attribute value as the second item.
            Attribute names and values are converted to Unicode strings.
        :returns: The created element.
        :rtype: :class:`Element`
        :raises ecoxipy.XMLWellFormednessException: If the ``name`` is not a
             valid XML name.
        '''
        attributes = kargs.get('attributes', {})
        return Element(_unicode(name),
            [
                child if isinstance(child, XMLNode) else Text.create(child)
                for child in children
            ],
            {} if attributes is None else {
                _unicode(attr_name): _unicode(attr_value)
                for attr_name, attr_value in attributes.items()
            }, True)

    def _set_namespace(self, prefix, value):
        self._namespace_prefix_to_uri[prefix] = value

    def _remove_namespace(self, prefix):
        del self._namespace_prefix_to_uri[prefix]
        prefix_targets = self._namespace_prefix_to_target[prefix]
        for target_id in prefix_targets:
            target = self._namespace_targets[target_id]
            target._clear_namespace_uri()

    def _register_namespace_target(self, target):
        prefix = target.namespace_prefix
        target_id = id(target)
        self._namespace_targets[target_id] = target
        try:
            prefix_targets = self._namespace_prefix_to_target[prefix]
        except KeyError:
            prefix_targets = set()
            self._namespace_prefix_to_target[prefix] = prefix_targets
        prefix_targets.add(target_id)

    def _remove_namespace_target(self, target):
        prefix = target.namespace_prefix
        target_id = id(target)
        del self._namespace_targets[target_id]
        prefix_targets = self._namespace_prefix_to_target[prefix]
        prefix_targets.remove(target_id)
        if len(prefix_targets) == 0:
            del self._namespace_prefix_to_target[prefix]

    @property
    def namespace_prefixes(self):
        def iterator():
            current = self
            while isinstance(current, Element):
                for prefix in current._namespace_prefix_to_uri:
                    yield prefix
                current = current.parent
        return iterator()

    def _get_namespace(self, prefix):
        current = self
        while isinstance(current, Element):
            try:
                return current, current._namespace_prefix_to_uri[prefix]
            except KeyError:
                current = current.parent
        return None, False

    def get_namespace_prefix_element(self, prefix):
        return self._get_namespace(prefix)[0]

    def get_namespace_uri(self, prefix):
        return self._get_namespace(prefix)[1]

    @property
    def name(self):
        '''The name of the element.'''
        return self._name

    @name.setter
    def name(self, name):
        name = _unicode(name)
        if name == self._name:
            return
        if self._check_well_formedness:
            _helpers.enforce_valid_xml_name(name)
        self._name = name
        self._clear_namespace_properties()

    @property
    def attributes(self):
        '''\
        An :class:`Attributes` instance containing the element's attributes.
        '''
        return self._attributes

    def _create_str(self, out):
        return out.element(self.name, [
                child._create_str(out) for child in self
            ], self._attributes.to_dict())

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
        attributes = AttributesImpl(
            self._attributes.to_dict())
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
        return 'ecoxipy.pyxom.Element[{}, {{...}}]'.format(
            _string_repr(self._name))

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
            self._attributes.to_dict())


class ContentNode(XMLNode):
    '''\
    Represents a node with content.

    :param content: The content.
    :type content: Unicode string
    '''
    __slots__ = ('_content')

    def __init__(self, content):
        self._content = content

    @classmethod
    def create(cls, content):
        '''\
        Creates an instance of the :class:`ContentNode` implementation and
        converts ``content`` to an Unicode string.

        :param content: The content of the node. This will be converted to an
            Unicode string.
        :returns: The created :class:`ContentNode` implementation instance.
        '''
        return cls(_unicode(content))

    @property
    def content(self):
        return self._content

    @content.setter
    def content(self, value):
        self._content = _unicode(value)

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
        return 'ecoxipy.pyxom.Text({})'.format(_string_repr(self.content))

    def _create_sax_events(self, content_handler, indent):
        content_handler.characters(self.content)

    def _create_str(self, out):
        return out.text(self.content)

    def duplicate(self):
        return Text(self.content)


class Comment(ContentNode):
    '''\
    Represents a comment node.

    :param content: The content.
    :type content: Unicode string
    :raises ecoxipy.XMLWellFormednessException: If ``check_well_formedness``
        is :const:`True` and ``content`` is not valid.
    '''
    __slots__ = ('_check_well_formedness')

    def __init__(self, content, check_well_formedness=False):
        if check_well_formedness:
            _helpers.enforce_valid_comment(content)
        ContentNode.__init__(self, content)
        self._check_well_formedness = check_well_formedness

    @staticmethod
    def create(content):
        '''\
        Creates a comment node.

        :param content: The content of the comment. This will be converted to an
            Unicode string.
        :returns: The created commment node.
        :rtype: :class:`Comment`
        :raises ecoxipy.XMLWellFormednessException: If ``content`` is not
            valid.
        '''
        content = _unicode(content)
        return Comment(content, True)

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
        return 'ecoxipy.pyxom.Comment({})'.format(_string_repr(self.content))

    def duplicate(self):
        return Comment(self.content)

    @ContentNode.content.setter
    def content(self, content):
        content = _unicode(content)
        if self._check_well_formedness:
            _helpers.enforce_valid_comment(content)
        self._content = content


class ProcessingInstruction(ContentNode):
    '''\
    Represent a processing instruction.

    :param target: The processing instruction target.
    :param content: The processing instruction content or :const:`None`.
    :param check_well_formedness: If :const:`True` the target will be checked
        to be a valid XML name.
    :type check_well_formedness: :func:`bool`
    :raises ecoxipy.XMLWellFormednessException: If ``check_well_formedness``
        is :const:`True` and either the ``target`` or the ``content`` are not
        valid.
    '''
    __slots__ = ('_target', '_check_well_formedness')

    def __init__(self, target, content, check_well_formedness=False):
        if check_well_formedness:
            _helpers.enforce_valid_pi_target(target)
            if content is not None:
                _helpers.enforce_valid_pi_content(content)
        ContentNode.__init__(self, content)
        self._target = target
        self._check_well_formedness = check_well_formedness

    @staticmethod
    def create(target, content=None):
        '''\
        Creates a processing instruction node and converts the parameters to
        appropriate types.

        :param target: The target, will be converted to an Unicode string.
        :param content: The content, if it is not :const:`None` it will be
            converted to an Unicode string.
        :returns: The created processing instruction.
        :rtype: :class:`ProcessingInstruction`
        :raises ecoxipy.XMLWellFormednessException: If either the ``target``
            or the ``content`` are not valid.
        '''
        target = _unicode(target)
        if content is not None:
            content = _unicode(content)
        return ProcessingInstruction(target, content, True)

    @property
    def target(self):
        return self._target

    @target.setter
    def target(self, target):
        target = _unicode(target)
        if self._check_well_formedness:
            _helpers.enforce_valid_pi_target(target)
        self._target = _unicode(target)

    @ContentNode.content.setter
    def content(self, content):
        if content is not None:
            content = _unicode(content)
            if self._check_well_formedness:
                _helpers.enforce_valid_pi_content(content)
        self._content = content

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
        return 'ecoxipy.pyxom.ProcessingInstruction({}, {})'.format(
            _string_repr(self._target), _string_repr(self.content))

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

import ast

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
