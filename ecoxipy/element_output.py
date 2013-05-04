# -*- coding: utf-8 -*-
ur'''\

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
>>> element = b.article(
...     {'umlaut-attribute': u'äöüß', 'lang': 'de'},
...     b.h1(
...         b & '<Example>', # Explicitly insert text
...         data='to quote: <&>"\''
...     ),
...     b.p('Hello', b.em(' World'), '!'),
...     None,
...     b.div(
...         # Insert elements with special names using subscripts:
...         b['data-element'](u'äöüß <&>'),
...         # Import content by calling the builder:
...         b(
...             '<p attr="value">raw content</p>Some Text',
...             # Create an element without calling the creating method:
...             b.br,
...             (i for i in range(3))
...         ),
...         (i for i in range(3, 6))
...     ),
...     b | '<This is a comment!>',
...     b['pi-target':'<PI content>'],
...     b['pi-without-content':],
...     lang='en', count=1
... )


Getting the :func:`unicode` value of an :class:`XMLNode` creates a
XML Unicode string:

>>> document_string = u"""<article lang="en" count="1" umlaut-attribute="äöüß"><h1 data="to quote: &lt;&amp;&gt;&quot;'">&lt;Example&gt;</h1><p>Hello<em> World</em>!</p><div><data-element>äöüß &lt;&amp;&gt;</data-element><p attr="value">raw content</p>Some Text<br/>012345</div><!--<This is a comment!>--><?pi-target <PI content>?><?pi-without-content?></article>"""
>>> unicode(element) == document_string
True


Getting the :func:`str` value of an :class:`XMLNode` creates an `UTF-8`
encoded XML string:

>>> str(element) == document_string.encode('utf-8')
True


:class:`XMLNode` instances can also generate SAX events, see
:meth:`XMLNode.create_sax_events` (note that the default
:class:`xml.sax.ContentHandler` is :class:`xml.sax.saxutils.ContentHandler`,
which does not support comments):

>>> from StringIO import StringIO
>>> string_out = StringIO()
>>> content_handler = element.create_sax_events(out=string_out)
>>> string_out.getvalue() == u"""<article lang="en" count="1" umlaut-attribute="äöüß"><h1 data="to quote: &lt;&amp;&gt;&quot;'">&lt;Example&gt;</h1><p>Hello<em> World</em>!</p><div><data-element>äöüß &lt;&amp;&gt;</data-element><p attr="value">raw content</p>Some Text<br></br>012345</div><?pi-target <PI content>?><?pi-without-content ?></article>""".encode('utf-8')
True
>>> string_out.close()


You can also create indented XML when calling the
:meth:`XMLNode.__unicode__` and :meth:`XMLNode.__str__` by supplying the
``indent_incr`` argument:

>>> indented_document_string = u"""\
... <article lang="en" count="1" umlaut-attribute="äöüß">
...     <h1 data="to quote: &lt;&amp;&gt;&quot;'">
...         &lt;Example&gt;
...     </h1>
...     <p>
...         Hello
...         <em>
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
>>> string_out = StringIO()
>>> content_handler = element.create_sax_events(indent_incr='    ', out=string_out)
>>> string_out.getvalue() == indented_document_string.encode('utf-8')
True
>>> string_out.close()



:class:`Output` Implementation
------------------------------

.. autoclass:: ecoxipy.element_output.ElementOutput


Representation
--------------

.. autoclass:: ecoxipy.element_output.XMLNode
    :special-members: __str__, __unicode__

.. autoclass:: ecoxipy.element_output.Element

.. autoclass:: ecoxipy.element_output.Attributes

.. autoclass:: ecoxipy.element_output.Comment

.. autoclass:: ecoxipy.element_output.ProcessingInstruction
'''

from abc import ABCMeta, abstractmethod
from xml import dom
from xml.dom import minidom
from xml.sax.saxutils import XMLGenerator
from xml.sax.xmlreader import AttributesImpl
from StringIO import StringIO

from tinkerpy import ImmutableDict

from . import Output
from dom_output import _dom_create_element
from string_output import StringOutput as _StringOutput


class ElementOutput(Output):
    '''\
    An :class:`Output` implementation which creates :class:`Element`
    instances and :func:`str` instances. :func:`unicode` instances are
    encoded as UTF-8.
    '''

    def element(self, name, children, attributes):
        '''\
        Returns a :class:`Element`.

        :param name: The name of the element to create.
        :param children: The iterable of children to add to the element to
            create.
        :param attributes: The mapping of arguments of the element to create.
        :returns: The element created.
        :rtype: :class:`Element`
        '''
        return Element(name, children, attributes)

    def embed(self, content):
        '''\
        Parses the non-:class:`Element` elements of ``content`` as XML and
        returns an a :func:`list` of :class:`Element` and :func:`unicode`
        instances or a single instance.

        :param content: XML strings and/or elements.
        :returns: The elements parsed or a single element.
        :raises xml.parsers.expat.ExpatError: If XML is not well-formed.
        :returns:
            :class:`Element` or a :func:`list` of :class:`Element` instances
        '''
        imported_content = []

        def import_xml(text):
            def import_element(children_list, element):
                name = element.tagName
                children = []
                import_nodes(children, element.childNodes)
                attributes = import_attributes(element)
                imported_element = Element(name, children, attributes)
                children_list.append(imported_element)

            def import_text(children_list, text):
                children_list.append(text.data.encode('UTF-8'))

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
                    if node.nodeType == dom.Node.ELEMENT_NODE:
                        import_element(children_list, node)
                    elif node.nodeType in [dom.Node.TEXT_NODE,
                            dom.Node.CDATA_SECTION_NODE]:
                        import_text(children_list, node)
                    elif (node.nodeType ==
                            dom.Node.PROCESSING_INSTRUCTION_NODE):
                        import_processing_instruction(children_list, node)
                    elif (node.nodeType == dom.Node.COMMENT_NODE):
                        import_comment(children_list, node)

            document = minidom.parseString('<ROOT>' + text + '</ROOT>')
            import_nodes(imported_content,
                document.documentElement.childNodes)

        for content_item in content:
            if isinstance(content_item, Element):
                imported_content.append(content_item)
            else:
                if not isinstance(content_item, (str, unicode)):
                    content_item = unicode(content_item)
                if isinstance(content_item, unicode):
                    content_item = content_item.encode('utf-8')
                if isinstance(content_item, str):
                    import_xml(content_item)
        if len(imported_content) == 1:
            return imported_content[0]
        return imported_content

    def text(self, content):
        '''\
        Creates :func:`str` instances from the items of ``content``.

        :param content: The list of texts.
        :returns: A list of :func:`unicode` instances.
        '''
        imported = []
        for content_item in content:
            if not isinstance(content_item, (str, unicode)):
                content_item = unicode(content_item)
            if isinstance(content_item, unicode):
                content_item = content_item.encode('UTF-8')
            imported.append(content_item)
        if len(imported) == 1:
            return imported[0]
        return imported

    def comment(self, content):
        '''\
        Creates a :class:`Comment`.

        :param content: The content of the comment.
        :type content: :func:`str` or :func:`unicode`
        :returns:
            The created comment.
        '''
        return Comment(content)

    def processing_instruction(self, target, content):
        '''\
        Creates a :class:`ProcessingInstruction`.

        :param target: The target of the processing instruction.
        :type target: :func:`str` or :func:`unicode`
        :param content: The content of the processing instruction.
        :type content: :func:`str` or :func:`unicode`
        :returns:
            The created processing instruction.
        '''
        return ProcessingInstruction(target, content)


class XMLNode(object):
    '''\
    Base class for XML node objects.
    '''
    __metaclass__ = ABCMeta

    def __str__(self):
        '''\
        Creates a string containing the XML representation of the node.

        :returns: The XML representation of the node as a :func:`str`
            instance with encoding `UTF-8`.
        '''
        return self.create_str(encoding='UTF-8')

    def __unicode__(self):
        '''\
        Creates a string containing the XML representation of the node.

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
            :func:`unicode` output.
        '''
        if out is None:
            out = _StringOutput(out_encoding=encoding)
        return self._create_str(out, encoding)

    @abstractmethod
    def _create_str(self, out, encoding):
        '''\
        Creates a string containing the XML representation of the node.

        :param out: A :class:`ecoxipy.string_output.StringOutput` instance.
        :param encoding: The output encoding or :const:`None` for
            :func:`unicode` output.
        '''
        pass

    def create_sax_events(self, content_handler=None, out=None,
            out_encoding=None, indent_incr=None):
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
            content_handler = XMLGenerator(out, out_encoding)
        if indent_incr is None:
            indent = False
        else:
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
    '''

    __slots__ = ('_name', '_children', '_attributes')

    def __init__(self, name, children, attributes):
        self._name = unicode(name)
        self._children = tuple(children)
        self._attributes = Attributes(attributes)

    @property
    def name(self):
        '''The name of the element.'''
        return self._name

    @property
    def children(self):
        '''\
        A :func:`tuple` of the contained content (:class:`Element`
        instances or :func:`unicode` instances).
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

    def _create_str(self, out, encoding):
        return out.element(self.name, [
                    child._create_str(out, encoding)
                    if isinstance(child, XMLNode) else child
                for child in self.children
            ], self.attributes)

    def _create_dom_children(self, document):
        '''\
        Creates DOM children using the supplied ``document``.

        :param document: The DOM document to use as the node factory.
        :returns: The created children list.
        '''
        children = [
            child.create_dom_element(document)
            if isinstance(child, Element)
            else document.createTextNode(unicode(child))
            for child in self.children
        ]
        return children

    def create_dom_element(self, document):
        '''\
        Creates a DOM element representing the element.

        :param document: The document to create DOM nodes with.
        :type document: :class:`xml.dom.Document`
        :returns: The created DOM element.
        '''
        children = self._create_dom_children(document)
        element = _dom_create_element(document, self.name, self.attributes,
            children)
        return element

    def create_dom_document(self, dom_implementation=None):
        '''\
        Creates a DOM document with the document element
        representing the element.

        :param dom_implementation: The DOM implementation to use to create a
            document. If this is :const:`None`, one is created using
            :func:`xml.dom.minidom.getDOMImplementation()`.
        :type dom_implementation: :class:`xml.dom.DOMImplementation`
        :returns: The created DOM document.
        '''
        if dom_implementation is None:
            dom_implementation = minidom.getDOMImplementation()
        document = dom_implementation.createDocument(None, None, None)
        element = self.create_dom_element(document)
        return document

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
        attributes = AttributesImpl(self.attributes)
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
                content_handler.characters(unicode(child))
                last_event_characters = True
        if len(self.children) > 0:
            do_indent()
        content_handler.endElement(self.name)
        if indent and indent_count == 0:
            content_handler.characters('\n')


class Attributes(ImmutableDict):
    u'''\
    An immutable dictionary representing XML attributes. For attribute names
    (keys) and values their :func:`unicode` representation is used in all
    places.

    Usage examples:

    >>> attrs = Attributes({
    ...     'foo': 'bar', 'one': 1, u'äöüß': 'umlauts', 'umlauts': u'äöüß'
    ... })
    >>> attrs['foo']
    u'bar'
    >>> len(attrs)
    4
    >>> 'foo' in attrs
    True
    >>> for name, value in attrs.items(): print u'{}: {}'.format(name, value)
    umlauts: äöüß
    foo: bar
    äöüß: umlauts
    one: 1
    '''
    def __init__(self, *args, **kargs):
        self._dict = dict(*args, **kargs)
        for name, value in self._dict.items():
            unicode_name = unicode(name)
            unicode_value = unicode(value)
            if not isinstance(name, unicode):
                del self._dict[name]
            if value != unicode_value or unicode_name not in self._dict:
                self._dict[unicode_name] = unicode_value

    def __getitem__(self, name):
        return ImmutableDict.__getitem__(self, unicode(name))


class Comment(XMLNode):
    __slots__ = ('_content')

    def __init__(self, content):
        if not isinstance(content, (str, unicode)):
            content = unicode(content)
        self._content = content

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
    __slots__ = ('_target', '_content')

    def __init__(self, target, content):
        if not isinstance(target, (str, unicode)):
            target = unicode(target)
        if not isinstance(content, (str, unicode)):
            content = unicode(content)
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
        content_handler.processingInstruction(self.target, self._content)
