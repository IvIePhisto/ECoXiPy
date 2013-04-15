# -*- coding: utf-8 -*-

'''\
This package provides facilities to easily build `XML
<http://www.w3.org/XML/>` documents.
'''

import inspect
import re
import collections
from abc import ABCMeta, abstractmethod

from xml.sax.saxutils import XMLGenerator, escape, quoteattr
from xml.sax.xmlreader import AttributesImpl
from xml import dom
from xml.dom import minidom

from StringIO import StringIO


class MarkupBuilder(object):
    ur'''\
    A builder for creating XML in a pythonic way.

    :param output:

        The output to use. If this is :const:`None` the default output
        :class:`ecoxipy.element_output.ElementOutput` is used.

    :type output: The :class:`Output` to use.

    :raises: :class:`TypeError` if ``output`` is of the wrong type.


    Each attribute access on an instance of this class returns a method which
    on calling creates an element in the output representation determined by
    the used :class:`Output` subclass instance. The name of the element is the
    same as the name of the attribute. Its children are the positional
    arguments, the attributes are determined by the named attributes. These
    `virtual` (not in the C sense) methods have the following signature (with
    ``element_name`` being substituted by the name of the element to create):


    .. method:: method_name(self, *children, **attributes)

        Creates an element in the output representation with the name being
        ``method_name``.

        :param children:

            The children (text, elements, attribute mappings and children
            lists) of the element.

        :param attributes:

            Each entry of this mapping defines an attribute of the created
            element, the name being the key and the value being the value
            identified by the key. The keys and values should be :class:`str`
            or :class:`unicode` instances.

        Those elements of ``children`` which are iterable mapping types
        (``child[name] for name in child``) define attributes. The entries of
        ``attributes`` overwrite entries from ``children`` elements.

        Those other elements of ``children`` which are iterable or iterators
        are replaced with their elements, callables are replaced with the
        result of the call.


    As this way not all element names can be used, you can retrieve a
    building method using the subscript syntax. If such a method is given as a
    child, it is called while building. This way creating elements without
    children or attributes is shorter.

    You can also call :class:`MarkupBuilder` instances. As with the
    ``children`` argument of the builders dynamic methods, those elements of
    the argument list, which are iterable or iterators, are unpacked. Those
    arguments which are callables are replaced by the result of the call. The
    :class:`MarkupBuilder` instance call returns a
    :class:`Output`-implementation-dependant representation for the list
    of arguments. In this process the arguments are parsed, converted,
    encoded or kept the same, depending on their type and the
    :class:`Output` implementation.


    Examples:

    >>> b = MarkupBuilder()
    >>> element = b.article(
    ...     {'umlaut-attribute': u'äöüß', 'lang': 'de'},
    ...     b.h1('<Example>', data='to quote: <&>"\''),
    ...     b.p('Hello ', b.em('World'), '!'),
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


    Getting the :class:`unicode` value of an :class:`Element` creates an
    XML unicode string:

    >>> document_string = u"""<article count="1" lang="en" umlaut-attribute="äöüß"><h1 data="to quote: &lt;&amp;&gt;&quot;'">&lt;Example&gt;</h1><p>Hello <em>World</em>!</p><div><data-element>äöüß &lt;&amp;&gt;</data-element><p attr="value">raw content</p>Some Text<br/>012345</div></article>"""
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
    ...             World
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
    >>> element.__unicode__(indent_incr='    ') == indented_document_string
    True
    >>> element.__str__(indent_incr='    ') == indented_document_string.encode('utf-8')
    True


    :class:`Element` instances can also generate SAX events (with
    :meth:`Element.create_sax_events`):

    >>> from StringIO import StringIO
    >>> string_out = StringIO()
    >>> content_handler = element.create_sax_events(out=string_out)
    >>> string_out.getvalue() == u"""<article lang="en" count="1" umlaut-attribute="äöüß"><h1 data="to quote: &lt;&amp;&gt;&quot;'">&lt;Example&gt;</h1><p>Hello <em>World</em>!</p><div><data-element>äöüß &lt;&amp;&gt;</data-element><p attr="value">raw content</p>Some Text<br></br>012345</div></article>""".encode('utf-8')
    True
    >>> string_out.close()
    >>> string_out = StringIO()
    >>> content_handler = element.create_sax_events(indent_incr='    ', out=string_out)
    >>> string_out.getvalue() == u"""\
    ... <article lang="en" count="1" umlaut-attribute="äöüß">
    ...     <h1 data="to quote: &lt;&amp;&gt;&quot;'">&lt;Example&gt;</h1>
    ...     <p>Hello
    ...         <em>World</em>!
    ...     </p>
    ...     <div>
    ...         <data-element>äöüß &lt;&amp;&gt;</data-element>
    ...         <p attr="value">raw content</p>Some Text
    ...         <br></br>012345
    ...     </div>
    ... </article>\
    ... """.encode('utf-8')
    True


    :class:`ecoxipy.dom_output.DOMOutput` creates DOM structures:

    >>> from ecoxipy.dom_output import DOMOutput
    >>> dom_output = DOMOutput()
    >>> doc = dom_output.document
    >>> b = MarkupBuilder(dom_output)
    >>> element = b.section(b.p('Hello World!'), None, b.p(u'äöüß'), b.p('<&>'), b('<raw/>text', b.br, (str(i) for i in range(3)), (str(i) for i in range(3, 6))), attr='\'"<&>')
    >>> element.toxml() == u"""<section attr="'&quot;&lt;&amp;&gt;"><p>Hello World!</p><p>äöüß</p><p>&lt;&amp;&gt;</p><raw/>text<br/>012345</section>"""
    True


    :class:`ecoxipy.string_output.StringOutput` creates strings of encoded
    XML and is aimed at high performance by using string concatenation:

    >>> from ecoxipy.string_output import StringOutput
    >>> xml_output = StringOutput(out_encoding=None)
    >>> b = MarkupBuilder(xml_output)
    >>> xml = b.section(b.p('Hello World!'), None, b.p(u'äöüß'), b.p('<&>'), b('<raw/>text', b.br, (str(i) for i in range(3)), (str(i) for i in range(3, 6))), attr='\'"<&>')
    >>> xml == u"""<section attr="'&quot;&lt;&amp;&gt;"><p>Hello World!</p><p>äöüß</p><p>&lt;&amp;&gt;</p><raw/>text<br/>012345</section>"""
    True


    Using :func:`markup_builder_namespace` to decorate functions or methods
    makes it even more convenient to use :class:`MarkupBuilder`, but the
    allowed elements have to be defined:

    >>> builds_html = markup_builder_namespace(StringOutput, 'section', 'p', 'br', _=b)
    >>> @builds_html
    ... def view(value):
    ...     return section(
    ...         p(value),
    ...         None,
    ...         p(u'äöüß'),
    ...         p('<&>'),
    ...         _('<raw/>text', br, (str(i) for i in range(3))),
    ...         (str(i) for i in range(3, 6)),
    ...         attr='\'"<&>'
    ...     )
    ...
    >>> view('Hello World!') == u"""<section attr="'&quot;&lt;&amp;&gt;"><p>Hello World!</p><p>äöüß</p><p>&lt;&amp;&gt;</p><raw/>text<br/>012345</section>"""
    True
    '''

    def __init__(self, output=None):
        if output is None:
            from element_output import ElementOutput
            output = ElementOutput()
        else:
            if not isinstance(output, Output):
                raise TypeError('A "wob2.web.markup.Output" object must be given.')
        self._output = output

    @classmethod
    def _preprocess(cls, content, target_list, target_attributes=None):
        if content is None:
            return
        if isinstance(content, str) or isinstance(content, unicode):
            target_list.append(content)
        elif (target_attributes is not None
                and isinstance(content, collections.Mapping)):
            for key in content:
                value = content[key]
                if value is not None:
                    target_attributes[key] = content[key]
        elif isinstance(content, (collections.Sequence, collections.Iterable)):
            for value in content:
                if value is not None:
                    target_list.append(value)
        elif isinstance(content, collections.Callable):
            value = content()
            if value is not None:
                target_list.append(value)
        else:
            target_list.append(content)

    def __call__(self, *content):
        processed_content = []
        for content_element in content:
            self._preprocess(content_element, processed_content)
        return self._output.embed(*processed_content)

    def __getitem__(self, name):
        def parse_arguments(children, attributes):
            '''\
            Creates a children :class:`list` and an attributes :class:`dict`.

            :param children:
                text, elements, attribute mappings and children lists
            :type children:
                an iterable over items [``for child in children``]
            :param attributes: the main attributes
            :type attributes:
                an iterable mapping [``attributes[name] for name in
                attributes``]
            :returns:
                a :class:`tuple` of a :class:`list` at index 0 of children and
                a :class:`dict` at index 1 of attributes

            Those elements of ``children`` which are iterable mapping types
            (``child[name] for name in child``) are not returned in the
            children list but their entries define entries of the returned
            attributes dictionary. Other elements which are iterable or
            iterators are replaced with their elements, callables are replaced
            by the result of their call. The entries of ``attributes``
            complement the returned dictionary or overwrite entries from
            ``children`` elements.
            '''
            new_children = []
            new_attributes = dict()
            for child in children:
                self._preprocess(child, new_children, new_attributes)
            for name in attributes:
                new_attributes[name] = attributes[name]
            return (new_children, new_attributes)

        def build(*children, **attributes):
            return self._output.element(
                name,
                *parse_arguments(children, attributes)
            )
        return build

    def __getattr__(self, name):
        return self[name]


class Output(object):
    '''\
    Abstract class defining the :class:`MarkupBuilder` output interface.

    The abstract methods are called by :class:`MarkupBuilder` instances to
    create an element (:meth:`element`) or to add raw data (:meth:`raw`).
    '''
    __metaclass__ = ABCMeta

    @abstractmethod
    def element(self, name, children, attributes):
        '''\
        Abstract method, override in implementation class. This is called by
        :class:`MarkupBuilder` instances.

        :param name: The name of the element to create.
        :type name: :class:`str` or :class:`unicode`
        :param children: The iterable of children to add to the element to
            create.
        :param attributes: The mapping of attributes of the element to create.
        :returns: The element representation created.
        '''

    @abstractmethod
    def embed(self, *content):
        '''Imports the elements of ``content`` as data in the output
        representation.

        :param content: The data to parse.
        :type content: depends on :class:`Output` implementation
        :returns:
            a list of children or a single child in output representation
        '''


def markup_builder_namespace(output, *element_names, **kargs):
    '''\
    Creates a :class:`MarkupBuilder` instance with a new instance of the given
    ``output`` class. Using :func:`tinkerpy.namespace` all in
    ``element_names`` defined names are bound to the appropriate `virtual`
    methods of the created builder.

    :param output: The :class:`Output` class to use.
    :param element_names: The names to bind to the appropriate `virtual`
        builder methods.
    :param kargs: Arguments passed to the ``output`` constructor.
    '''
    from tinkerpy import namespace
    builder = MarkupBuilder(output(**kargs))
    return namespace(builder,
        *element_names,
        _b=builder
    )
