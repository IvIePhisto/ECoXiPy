# -*- coding: utf-8 -*-
u'''\
:mod:`ecoxipy.pyxom` - Pythonic XML Object Model (PyXOM)
========================================================

This module implements the *Pythonic XML Object Model* (PyXOM) for the
representation of XML structures. To conveniently create PyXOM data structures
use :mod:`ecoxipy.pyxom.output`, for indexing use
:mod:`ecoxipy.pyxom.indexing` (if :attr:`Document.element_by_id` and
:attr:`Document.elements_by_name` are not enough for you).


.. _ecoxipy.pyxom.examples:

Examples
--------

XML Creation
^^^^^^^^^^^^

If you use the constructors be sure to supply the right data types, otherwise
use the :meth:`create` methods or use :class:`ecoxipy.MarkupBuilder`, which
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
...                 'foo:bar': 'Hello', 'id': 'foo'}
...         ),
...         {'xmlns': 'http://www.w3.org/1999/xhtml/'}
...     ), doctype_name='article', omit_xml_declaration=True
... )


Enforcing Well-Formedness
^^^^^^^^^^^^^^^^^^^^^^^^^

Using the :meth:`create` methods or passing the parameter
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
>>> list(document[0][2].descendants())
[ecoxipy.pyxom.Element['data-element', {...}], ecoxipy.pyxom.Text('\\xe4\\xf6\\xfc\\xdf <&>'), ecoxipy.pyxom.Element['p', {...}], ecoxipy.pyxom.Text('raw content'), ecoxipy.pyxom.Text('Some Text'), ecoxipy.pyxom.Element['br', {...}], ecoxipy.pyxom.Text('0'), ecoxipy.pyxom.Text('1'), ecoxipy.pyxom.Text('2'), ecoxipy.pyxom.Text('3'), ecoxipy.pyxom.Text('4'), ecoxipy.pyxom.Text('5')]

>>> list(document[0][-2].preceding_siblings)
[ecoxipy.pyxom.ProcessingInstruction('pi-target', '<PI content>'), ecoxipy.pyxom.Comment('<This is a comment!>'), ecoxipy.pyxom.Element['div', {...}], ecoxipy.pyxom.Element['p', {...}], ecoxipy.pyxom.Element['h1', {...}]]
>>> list(document[0][2][-1].preceding)
[ecoxipy.pyxom.Text('4'), ecoxipy.pyxom.Text('3'), ecoxipy.pyxom.Text('2'), ecoxipy.pyxom.Text('1'), ecoxipy.pyxom.Text('0'), ecoxipy.pyxom.Element['br', {...}], ecoxipy.pyxom.Text('Some Text'), ecoxipy.pyxom.Element['p', {...}], ecoxipy.pyxom.Element['data-element', {...}], ecoxipy.pyxom.Element['p', {...}], ecoxipy.pyxom.Element['h1', {...}]]

>>> list(document[0][0].following_siblings)
[ecoxipy.pyxom.Element['p', {...}], ecoxipy.pyxom.Element['div', {...}], ecoxipy.pyxom.Comment('<This is a comment!>'), ecoxipy.pyxom.ProcessingInstruction('pi-target', '<PI content>'), ecoxipy.pyxom.ProcessingInstruction('pi-without-content', None), ecoxipy.pyxom.Element['foo:somexml', {...}]]
>>> list(document[0][1][0].following)
[ecoxipy.pyxom.Element['em', {...}], ecoxipy.pyxom.Text('!'), ecoxipy.pyxom.Element['div', {...}], ecoxipy.pyxom.Comment('<This is a comment!>'), ecoxipy.pyxom.ProcessingInstruction('pi-target', '<PI content>'), ecoxipy.pyxom.ProcessingInstruction('pi-without-content', None), ecoxipy.pyxom.Element['foo:somexml', {...}]]


Descendants and children can also be retrieved in reverse document order:

>>> list(document[0][1].children(True)) == list(reversed(list(document[0][1].children())))
True
>>> list(document[0][2].descendants(True))
[ecoxipy.pyxom.Text('5'), ecoxipy.pyxom.Text('4'), ecoxipy.pyxom.Text('3'), ecoxipy.pyxom.Text('2'), ecoxipy.pyxom.Text('1'), ecoxipy.pyxom.Text('0'), ecoxipy.pyxom.Element['br', {...}], ecoxipy.pyxom.Text('Some Text'), ecoxipy.pyxom.Element['p', {...}], ecoxipy.pyxom.Text('raw content'), ecoxipy.pyxom.Element['data-element', {...}], ecoxipy.pyxom.Text('\\xe4\\xf6\\xfc\\xdf <&>')]


Normally :meth:`~ContainerNode.descendants` traverses the XML tree depth-first,
but you can also use breadth-first traversal:

>>> list(document[0][2].descendants(depth_first=False))
[ecoxipy.pyxom.Element['data-element', {...}], ecoxipy.pyxom.Element['p', {...}], ecoxipy.pyxom.Text('Some Text'), ecoxipy.pyxom.Element['br', {...}], ecoxipy.pyxom.Text('0'), ecoxipy.pyxom.Text('1'), ecoxipy.pyxom.Text('2'), ecoxipy.pyxom.Text('3'), ecoxipy.pyxom.Text('4'), ecoxipy.pyxom.Text('5'), ecoxipy.pyxom.Text('\\xe4\\xf6\\xfc\\xdf <&>'), ecoxipy.pyxom.Text('raw content')]
>>> list(document[0][2].descendants(True, False))
[ecoxipy.pyxom.Text('5'), ecoxipy.pyxom.Text('4'), ecoxipy.pyxom.Text('3'), ecoxipy.pyxom.Text('2'), ecoxipy.pyxom.Text('1'), ecoxipy.pyxom.Text('0'), ecoxipy.pyxom.Element['br', {...}], ecoxipy.pyxom.Text('Some Text'), ecoxipy.pyxom.Element['p', {...}], ecoxipy.pyxom.Element['data-element', {...}], ecoxipy.pyxom.Text('raw content'), ecoxipy.pyxom.Text('\\xe4\\xf6\\xfc\\xdf <&>')]


Normally :meth:`~ContainerNode.descendants` can also be given a depth limit:

>>> list(document[0].descendants(max_depth=2))
[ecoxipy.pyxom.Element['h1', {...}], ecoxipy.pyxom.Text('<Example>'), ecoxipy.pyxom.Element['p', {...}], ecoxipy.pyxom.Text('Hello'), ecoxipy.pyxom.Element['em', {...}], ecoxipy.pyxom.Text('!'), ecoxipy.pyxom.Element['div', {...}], ecoxipy.pyxom.Element['data-element', {...}], ecoxipy.pyxom.Element['p', {...}], ecoxipy.pyxom.Text('Some Text'), ecoxipy.pyxom.Element['br', {...}], ecoxipy.pyxom.Text('0'), ecoxipy.pyxom.Text('1'), ecoxipy.pyxom.Text('2'), ecoxipy.pyxom.Text('3'), ecoxipy.pyxom.Text('4'), ecoxipy.pyxom.Text('5'), ecoxipy.pyxom.Comment('<This is a comment!>'), ecoxipy.pyxom.ProcessingInstruction('pi-target', '<PI content>'), ecoxipy.pyxom.ProcessingInstruction('pi-without-content', None), ecoxipy.pyxom.Element['foo:somexml', {...}], ecoxipy.pyxom.Element['foo:somexml', {...}], ecoxipy.pyxom.Element['somexml', {...}], ecoxipy.pyxom.Element['bar:somexml', {...}]]
>>> list(document[0].descendants(depth_first=False, max_depth=2))
[ecoxipy.pyxom.Element['h1', {...}], ecoxipy.pyxom.Element['p', {...}], ecoxipy.pyxom.Element['div', {...}], ecoxipy.pyxom.Comment('<This is a comment!>'), ecoxipy.pyxom.ProcessingInstruction('pi-target', '<PI content>'), ecoxipy.pyxom.ProcessingInstruction('pi-without-content', None), ecoxipy.pyxom.Element['foo:somexml', {...}], ecoxipy.pyxom.Text('<Example>'), ecoxipy.pyxom.Text('Hello'), ecoxipy.pyxom.Element['em', {...}], ecoxipy.pyxom.Text('!'), ecoxipy.pyxom.Element['data-element', {...}], ecoxipy.pyxom.Element['p', {...}], ecoxipy.pyxom.Text('Some Text'), ecoxipy.pyxom.Element['br', {...}], ecoxipy.pyxom.Text('0'), ecoxipy.pyxom.Text('1'), ecoxipy.pyxom.Text('2'), ecoxipy.pyxom.Text('3'), ecoxipy.pyxom.Text('4'), ecoxipy.pyxom.Text('5'), ecoxipy.pyxom.Element['foo:somexml', {...}], ecoxipy.pyxom.Element['somexml', {...}], ecoxipy.pyxom.Element['bar:somexml', {...}]]


Namespaces
""""""""""

PyXOM supports the interpretation of `Namespaces in XML
<http://www.w3.org/TR/REC-xml-names/>`_. Namespace prefix and local names are
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
:attr:`Attribute.namespace_uri` (originally defined as
:attr:`NamespaceNameMixin.namespace_uri`), these properties look up the
namespace prefix of the node in the parent elements (this information is
cached, so don't fear multiple retrieval):

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


Indexes
"""""""

On :class:`Document` instances :class:`ecoxipy.pyxom.indexing.IndexDescriptor`
attributes are defined for fast retrieval (after initially building the
index).

Use :attr:`~Document.element_by_id` to get elements by the value of their
``id`` attribute:

>>> document.element_by_id['foo'] is document[0][-1]
True
>>> 'bar' in document.element_by_id
False


:attr:`~Document.elements_by_name` allows retrieval of elements by their name:

>>> document[0][-1] in list(document.elements_by_name['foo:somexml'])
True
>>> 'html' in document.elements_by_name
False


Retrieve elements and attributes by their namespace data by using
:attr:`~Document.nodes_by_namespace`:

>>> from functools import reduce
>>> elements_and_attributes = set(
...     filter(lambda node: isinstance(node, Element),
...         document.descendants()
...     )
... ).union(
...     reduce(lambda x, y: x.union(y),
...         map(lambda node: set(node.attributes.values()),
...             filter(lambda node: isinstance(node, Element),
...                 document.descendants()
...             )
...         )
...     )
... )
>>> set(document.nodes_by_namespace()) == set(filter(
...     lambda node: node.namespace_uri is not False,
...     elements_and_attributes
... ))
True
>>> set(document.nodes_by_namespace('foo://bar')) == set(filter(
...     lambda node: node.namespace_uri == u'foo://bar',
...     elements_and_attributes
... ))
True
>>> set(document.nodes_by_namespace(local_name='bar')) == set(filter(
...     lambda node: node.local_name == u'bar',
...     elements_and_attributes
... ))
True
>>> set(document.nodes_by_namespace('foo://bar', 'bar')) == set(filter(
...     lambda node: node.namespace_uri == u'foo://bar' and node.local_name == u'bar',
...     elements_and_attributes
... ))
True

Manipulation and Equality
^^^^^^^^^^^^^^^^^^^^^^^^^

All :class:`XMLNode` instances have attributes which allow for modification.
:class:`Document` and :class:`Element` instances also allow modification of
their contents like sequences.


Duplication and Comparisons
"""""""""""""""""""""""""""

Use :meth:`XMLNode.duplicate` to create a deep copy of a XML node:

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

The attributes of an :class:`Element` instance are available as
:attr:`Element.attributes`. This is an :class:`Attributes` instance which
contains :class:`Attribute` instances:

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
>>> document_copy[0][0].attributes['data'].value = old_data
>>> document == document_copy
True
>>> document != document_copy
False


:class:`Attributes` instances allow for creation of :class:`Attribute`
instances:

>>> somexml = document_copy[0][-1]
>>> foo_attr = somexml[0].attributes.create_attribute('foo:foo', 'bar')
>>> foo_attr is somexml[0].attributes['foo:foo']
True
>>> foo_attr == somexml[0].attributes['foo:foo']
True
>>> foo_attr != somexml[0].attributes['foo:foo']
False
>>> 'foo:foo' in somexml[0].attributes
True
>>> foo_attr.namespace_uri == u'foo://bar'
True


Attributes may be removed:

>>> somexml[0].attributes.remove(foo_attr)
>>> 'foo:foo' in somexml[0].attributes
False
>>> foo_attr.parent == None
True
>>> foo_attr.namespace_uri == False
True


You can also add an attribute to an element's attributes, it is automatically
moved if it belongs to another element's attributes:

>>> somexml[0].attributes.add(foo_attr)
>>> 'foo:foo' in somexml[0].attributes
True
>>> foo_attr.parent == somexml[0].attributes
True
>>> foo_attr.parent != somexml[0].attributes
False
>>> foo_attr.namespace_uri == u'foo://bar'
True
>>> del somexml[0].attributes['foo:foo']
>>> 'foo:foo' in somexml[0].attributes
False
>>> attr = document[0][-1].attributes['foo:bar']
>>> attr.name = 'test'
>>> attr.namespace_prefix is None
True
>>> print(attr.local_name)
test


Documents and Elements
""""""""""""""""""""""

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
>>> p_element in document_copy[0]
False
>>> p_element.namespace_uri == False
True
>>> document_copy[0][0].append(p_element)
>>> document_copy[0][0][-1] is p_element
True
>>> p_element in document_copy[0][0]
True
>>> p_element.namespace_uri == u'http://www.w3.org/1999/xhtml/'
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


Indexes and Manipulation
""""""""""""""""""""""""

If a document is modified, the indexes should be deleted. This can be done
using :func:`del` on the index attribute or calling
:meth:`~Document.delete_indexes`.

>>> del document_copy[0][-1]
>>> document_copy.delete_indexes()
>>> 'foo' in document_copy.element_by_id
False
>>> 'foo:somexml' in document_copy.elements_by_name
False


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

Document
^^^^^^^^

.. autoclass:: Document
.. autoclass:: DocumentType


Element
^^^^^^^

.. autoclass:: Element
.. autoclass:: Attribute
.. autoclass:: Attributes


Other Nodes
^^^^^^^^^^^

.. autoclass:: Text
.. autoclass:: Comment
.. autoclass:: ProcessingInstruction


Base Classes
^^^^^^^^^^^^

.. autoclass:: XMLNode
.. autoclass:: ContainerNode
.. autoclass:: ContentNode
.. autoclass:: NamespaceNameMixin
'''

from ._common import XMLNode, ContainerNode
from ._attributes import NamespaceNameMixin, Attribute, Attributes
from ._document import DocumentType, Document
from ._element import Element
from ._content_nodes import ContentNode, Text, Comment, ProcessingInstruction
