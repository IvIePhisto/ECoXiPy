# -*- coding: utf-8 -*-

ur'''\
Used with :class:`MarkupBuilder` :class:`ElementOutput` creates structures
consisting of :class:`Element` and :class:`Attributes` instances.


Basic Example:

>>> from ecoxipy import MarkupBuilder
>>> b = MarkupBuilder()
>>> element = b.article(
...     {'umlaut-attribute': u'äöüß', 'lang': 'de'},
...     b.h1('<Example>', data='to quote: <&>"\''),
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
...             (str(i) for i in range(3))
...         ),
...         (str(i) for i in range(3, 6))
...     ),
...     lang='en', count=1
... )


Getting the :class:`unicode` value of an :class:`Element` creates a
XML Unicode string:

>>> document_string = u"""<article count="1" lang="en" umlaut-attribute="äöüß"><h1 data="to quote: &lt;&amp;&gt;&quot;'">&lt;Example&gt;</h1><p>Hello<em> World</em>!</p><div><data-element>äöüß &lt;&amp;&gt;</data-element><p attr="value">raw content</p>Some Text<br/>012345</div></article>"""
>>> unicode(element) == document_string
True


Getting the :class:`str` value of an :class:`Element` creates an `UTF-8`
encoded XML string:

>>> str(element) == document_string.encode('utf-8')
True


You can also create indented XML when calling the
:meth:`Element.__unicode__` and :meth:`Element.__str__` by supplying the
``indent_incr`` argument:

>>> indented_document_string = u"""\
... <article count="1" lang="en" umlaut-attribute="äöüß">
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
...         <br/>
...         0
...         1
...         2
...         3
...         4
...         5
...     </div>
... </article>
... """
>>> indented_unicode = element.__unicode__(indent_incr='    ')
>>> for i in range(len(indented_document_string)):
...     if indented_document_string[i] != indented_unicode[i]:
...         print u'[{}]{} - {}'.format(i, ord(indented_document_string[i]), ord(indented_unicode[i]))
...         print '-----'
...         print indented_document_string[:i]
...         print '-----'
...         print indented_document_string[i:]
...         print '-----'
...         print indented_unicode[i:]
...         break
>>> element.__unicode__(indent_incr='    ') == indented_document_string
True
>>> element.__str__(indent_incr='    ') == indented_document_string.encode('utf-8')
True


:class:`Element` instances can also generate SAX events (with
:meth:`Element.create_sax_events`):

>>> from StringIO import StringIO
>>> string_out = StringIO()
>>> content_handler = element.create_sax_events(out=string_out)
>>> string_out.getvalue() == u"""<article lang="en" count="1" umlaut-attribute="äöüß"><h1 data="to quote: &lt;&amp;&gt;&quot;'">&lt;Example&gt;</h1><p>Hello<em> World</em>!</p><div><data-element>äöüß &lt;&amp;&gt;</data-element><p attr="value">raw content</p>Some Text<br></br>012345</div></article>""".encode('utf-8')
True
>>> string_out.close()
>>> string_out = StringIO()
>>> content_handler = element.create_sax_events(indent_incr='    ', out=string_out)
>>> string_out.getvalue() == u"""\
... <article lang="en" count="1" umlaut-attribute="äöüß">
...     <h1 data="to quote: &lt;&amp;&gt;&quot;'">&lt;Example&gt;</h1>
...     <p>Hello
...         <em> World</em>!
...     </p>
...     <div>
...         <data-element>äöüß &lt;&amp;&gt;</data-element>
...         <p attr="value">raw content</p>Some Text
...         <br></br>012345
...     </div>
... </article>\
... """.encode('utf-8')
True
'''

from xml import dom
from xml.dom import minidom
from xml.sax.saxutils import XMLGenerator
from xml.sax.xmlreader import AttributesImpl

from . import Output, _dom_create_element


class ElementOutput(Output):
    '''A :class:`Output` implementation which creates :class:`Element`
    instances and strings.
    '''
    def element(self, name, children, attributes):
        '''Returns a :class:`Element`.

        :param name: The name of the element to create.
        :type name: :class:`str`
        :param children: The iterable of children to add to the element to
            create.
        :param attributes: The mapping of arguments of the element to create.
        :returns: The element created.
        :rtype: :class:`Element`
        '''
        return Element(name, children, attributes)

    def embed(self, *content):
        '''Parses the non-:class:`Element` elements of ``content`` as XML and
        returns an a :class:`list` of :class:`Element` and :class:`unicode`
        instances or a single instance.

        :param content: XML strings and/or elements.
        :type content: :class:`Element`, :class:`str` or :class:`unicode`
        :returns: The elements parsed or a single element.
        :raises xml.parsers.expat.ExpatError: If XML is not well-formed.
        :rtype:
            :class:`Element` or a :class:`list` of :class:`Element` instances
        '''
        def import_xml(text):
            def import_element(element):
                name = element.tagName
                children = import_nodes(element.childNodes)
                attributes = import_attributes(element)
                imported_element = Element(name, children, attributes)
                return imported_element

            def import_text(text):
                return text.data

            def import_attributes(element):
                attributes = dict()
                for attr in element.attributes.values():
                    attributes[attr.name] = attr.value
                return attributes

            def import_node(node):
                if node.nodeType == dom.Node.ELEMENT_NODE:
                    return import_element(node)
                elif node.nodeType in [dom.Node.TEXT_NODE,
                        dom.Node.CDATA_SECTION_NODE]:
                    return import_text(node)
                return None

            def import_nodes(nodes):
                imported_nodes = []
                for node in nodes:
                    node = import_node(node)
                    if node is not None:
                        imported_nodes.append(node)
                return imported_nodes

            document = minidom.parseString('<ROOT>' + text + '</ROOT>')
            return import_nodes(document.documentElement.childNodes)

        imported_content = []
        for content_element in content:
            if isinstance(content_element, unicode):
                content_element = content_element.encode('utf-8')
            if isinstance(content_element, str):
                imported_content.extend(import_xml(content_element))
            elif isinstance(content_element, Element):
                imported_content.append(content_element)
        if len(imported_content) == 1:
            return imported_content[0]
        return imported_content


class Element(object):
    '''A markup element.

    If the :func:`str` or :func:`unicode` functions are used on a
    :class:`Element` instance, a XML document encoded as a UTF-8 :class:`str`
    instance or :class:`unicode` instance respectively is returned.

    :param name:
        The name of the element to create. It's unicode value will be used.

    :param children: The children of the element.
    :type children: an iterable of items
    :param attributes: The attributes of the element.
    :type attributes: an subscriptable iterable over keys
    '''
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
        '''A :class:`tuple` of the contained content (:class:`Element`
        instances or :class:`unicode` instances).
        '''
        return self._children

    @property
    def attributes(self):
        '''A :class:`Attributes` instance containing the element's attributes.
        The key represents an attribute's name, the value is the attribute's
        value.
        '''
        return self._attributes

    def __str__(self, indent_incr=None):
        '''Creates a string containing the XML representation of the element.

        :param indent_incr: If this is not :const:`None` this activates
            pretty printing. In this case it should be a string and it is used
            for indenting.
        :type indent_incr: :class:`str`
        :returns: The XML representation of the element as an :class:`str`
            instance with encoding `UTF-8`.
        '''
        document = self.create_dom_document()
        element = document.documentElement
        if indent_incr is None:
            xml = element.toxml(encoding='utf-8')
        else:
            xml = element.toprettyxml(indent_incr, encoding='utf-8')
        document.unlink()
        return xml

    def __unicode__(self, indent_incr=None):
        '''Creates a string containing the XML representation of the element.

        :param indent_incr: If this is not :const:`None` this activates
            pretty printing. In this case it should be a string and it is used
            for indenting.
        :type indent_incr: :class:`str`
        :returns: The XML representation of the element as an :class:`unicode`
            instance.
        '''
        return self.__str__(indent_incr).decode('utf-8')

    def _create_dom_children(self, document):
        '''Creates DOM children using the supplied ``document``.

        :param document: The DOM document to use as the node factory.
        :returns: The created children list.
        '''
        children = [
            document.createTextNode(child)
            if isinstance(child, str) or isinstance(child, unicode)
            else child.create_dom_element(document)
            for child in self.children
        ]
        return children

    def create_dom_element(self, document):
        '''Creates a DOM element representing the element.

        :param document: The document to create DOM nodes with.
        :type document: :class:`xml.dom.Document`
        :returns: The created DOM element.
        '''
        children = self._create_dom_children(document)
        element = _dom_create_element(document, self.name, self.attributes,
            children)
        return element

    def create_dom_document(self, dom_implementation=None):
        '''Creates a DOM document with the document element
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

    def _create_sax_events(self, content_handler, indent_incr, indent):
        '''Creates SAX events for the element.'''
        child_indent = None
        if indent_incr is not None:
            if indent != '':
                content_handler.characters('\n' + indent)
            child_indent = indent_incr + indent
        attributes = AttributesImpl(self.attributes)
        content_handler.startElement(self.name, attributes)
        has_element_children = False
        for child in self.children:
            if isinstance(child, str) or isinstance(child, unicode):
                content_handler.characters(child)
            else:
                child._create_sax_events(
                    content_handler, indent_incr, child_indent)
                has_element_children |= True
        if indent_incr is not None:
            if has_element_children:
                content_handler.characters('\n' + indent)
        content_handler.endElement(self.name)

    def create_sax_events(self, content_handler=None, out=None,
            indent_incr=None):
        '''Creates SAX events.

        :param content_handler: If this is :const:`None` a
            ``xml.sax.saxutils.XMLGenerator`` is created and used as the
            content handler. If in this case ``out`` is not :const:`None`,
            it is used for output.
        :type content_handler: :class:`xml.sax.ContentHandler`
        :param out: The output to write to if a ``content_handler`` is given.
            It should have a ``write`` method like files.
        :param indent_incr: If this is not :const:`None` this activates
            pretty printing. In this case it should be a string and it is used
            for indenting.
        :type indent_incr: :class:`str`
        :returns: The content handler used.
        '''
        if content_handler is None:
            content_handler = XMLGenerator(out, 'utf-8')
        indent = None
        if indent_incr is not None:
            indent = ''
        self._create_sax_events(content_handler, indent_incr, indent)
        return content_handler


class Attributes(object):
    u'''A mapping class representing attributes. For attribute names (keys)
    and values their :class:`unicode` representation is used in all places.

    :func:`len`, :const:`del`, :const:`in` and item getting and setting are
    :supported.

    :param attributes: Attributes to define on initialization.
    :type attributes: an subscriptable iterable over keys

    Usage examples:

    >>> attrs = Attributes({
    ...     'foo': 'bar', 'one': 1, u'äöüß': 'umlauts', 'umlauts': u'äöüß'
    ... })
    >>> attrs['foo']
    u'bar'
    >>> attrs['foo'] = 'Hello World!'
    >>> print attrs['foo']
    Hello World!
    >>> len(attrs)
    4
    >>> 'foo' in attrs
    True
    >>> del attrs['foo']
    >>> attrs['foo']
    Traceback (most recent call last):
    KeyError: u'foo'
    >>> len(attrs)
    3
    >>> 'foo' in attrs
    False
    >>> for name in attrs.keys(): print name
    umlauts
    äöüß
    one
    >>> for value in attrs.values(): print value
    äöüß
    umlauts
    1
    '''
    def __init__(self, attributes):
        self._dict = dict()
        for name in attributes:
            self[name] = attributes[name]

    def __len__(self):
        return len(self._dict)

    def __delitem__(self, name):
        del self._dict[unicode(name)]

    def __getitem__(self, name):
        return self._dict[unicode(name)]

    def __setitem__(self, name, value):
        self._dict[unicode(name)] = unicode(value)

    def __iter__(self):
        return self._dict.__iter__()

    def keys(self):
        '''Returns a :class:`list` of the names of the attributes.'''
        return self._dict.keys()

    def values(self):
        '''Returns a :class:`list` of the values of the attributes.'''
        return self._dict.values()

    def items(self):
        '''Returns a :class:`list` of :class:`tuple` instances containing
        the name of an attribute at index 0 and the value at index 1.
        '''
        return self._dict.items()
