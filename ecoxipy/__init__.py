# -*- coding: utf-8 -*-
'''\

:mod:`ecoxipy` - The ECoXiPy API
================================

The package :mod:`ecoxipy` contains the basic API for creating `XML
<http://www.w3.org/XML/>`_. The central :class:`MarkupBuilder` provides the
interface you use, through an instance of this class all XML creation is done.
An instance of :class:`Output` you give to the :class:`MarkupBuilder` (if you
don't an instance of :class:`ecoxipy.pyxom.output.PyXOMOutput` is created)
does all the actual work and creates data in its XML representation. This way
the same code can create XML as:

*   :mod:`ecoxipy.pyxom` structures, those can create :mod:`xml.sax` events or
    can be serialized to byte or Unicode strings, besides being easily
    navigateable.
*   Strings using :mod:`ecoxipy.string_output`.
*   :mod:`xml.dom` structures using :mod:`ecoxipy.dom_output`.
*   :mod:`xml.etree` structures using :mod:`ecoxipy.etree_output`.
*   Any other data you can think of by implementing your own :class:`Output`
    class.


XML Creation
------------

You use instances of :class:`MarkupBuilder` to create XML, which use the
:class:`Output` implementation given on initialization. The following
subsections explain how to use the builder.


.. _ecoxipy.MarkupBuilder.item_access:

Attribute and Item Retrieval - Elements
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Each failed attribute retrieval on an instance of :class:`MarkupBuilder`
returns a method, which on calling creates an element in the output
representation determined by the used :class:`Output` subclass instance. The
name of the element is the same as the name of the attribute. Its children are
the positional arguments, the attributes are determined by the named
attributes. These `virtual` (not in the C sense) methods have the following
signature (with ``element_name`` being substituted by the name of the element
to create):


.. method:: ecoxipy.MarkupBuilder.method_name(self, *children, **attributes)

    Creates an element in the output representation with the name
    ``method_name``.

    :param children:

        The children (text, elements, attribute mappings and children
        lists) of the element.

    :param attributes:

        Each entry of this mapping defines an attribute of the created
        element, the name being the key and the value being the value
        identified by the key.

    Those items of ``children``, which are iterable mapping types
    (``child[name] for name in child``) define attributes. The entries of
    ``attributes`` overwrite entries from ``children`` items.

    Those other items of ``children``, which are iterable or iterators
    are replaced with their items, callables are replaced with the
    result of their call. The same is true for all items of those, thus
    you have to make sure no indefinite recursion occurs.

    All children which are not of the output type are converted to a
    Unicode string (byte strings are decoded with the given input
    encoding) and create text nodes.


You should not create elements with names starting with ``_`` in this way, as
:class:`MarkupBuilder` instances may have such attributes, and only elements
with names conforming to the Python identifier syntax can be created using
attribute access. For creating such elements use the subscript syntax for
item access, which also returns an element-building function.


.. _ecoxipy.MarkupBuilder.slicing:

Slicing - Processing Instructions and Documents
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
On a :class:`MarkupBuilder` instance you can use slicing to create processing
instructions or documents.

You create processing instructions by using the slicing operator with a start
argument, which becomes the target. If the end argument is specified it
becomes the content. So the slice ``['xml-stylesheet':'href="style.css"']``
becomes a processing instruction with target ``xml-stylesheet`` and content
``href="style.css"``.

If the slicing start argument is not specified, a function creating a XML
document is returned. The arguments of that function become the document
root nodes. The slicing end argument (if specified) denotes the document
type declaration content. It can either be a 3-:func:`tuple` containing
the document element name, the public ID and the system ID or a single
object to be used as the document element name. If the slicing step
argument is :const:`True`, the XML declaration is omitted and the
document encoding is `UTF-8`. Otherwise the slicing step denotes the
document encoding and the XML declaration is not omitted. If no step is
specified, the encoding is `UTF-8` and the XML declaration is not
omitted. So the slice
``[:('html', '-//W3C//DTD XHTML 1.0 Strict//EN', 'http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd'):True]``
creates a XHTML 1.0 Strict document without a XML declaration.


.. _ecoxipy.MarkupBuilder.calling:

Calling - XML Fragments
^^^^^^^^^^^^^^^^^^^^^^^
You can also call :class:`MarkupBuilder` instances to parse XML fragments
(lists of XML Nodes). As with the ``children`` argument of the builder's
dynamic methods, the arguments are unpacked and converted to Unicode, but
here each of the Unicode strings is parsed as XML using
:class:`ecoxipy.parsing.XMLFragmentParser`. This will raise a
:class:`xml.sax.SAXException` if the XML is not well-formed.


.. _ecoxipy.MarkupBuilder.operators:

Operators - Text and Comments
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The following operators create special nodes from their argument on a
:class:`MarkupBuilder` instance:

``&``
    Creates a text node.

``|``
    Creates a comment.


Classes
-------

.. autoclass:: MarkupBuilder
    :special-members: __getitem__, __getattr__, __call__, __and__, __or__

.. autoclass:: Output

.. autoclass:: XMLWellFormednessException
'''

import sys
import collections
from abc import ABCMeta, abstractmethod

_python2 = sys.version_info[0] <= 2
_unicode = unicode if _python2 else str


class MarkupBuilder(object):
    u'''\
    A builder for creating XML in a pythonic way. All byte strings given are
    are decoded with the input encoding specified on instanciation.

    :param output:

        The output to use. If this is :const:`None`,
        :class:`ecoxipy.pyxom.output.PyXOMOutput` is used.

    :type output: :class:`Output`

    :param in_encoding:

        The input encoding to be used to decode byte strings to Unicode.

    :param parser:

        The SAX parser to use for parsing XML. If it is :const:`None` the
        default of :class:`ecoxipy.XMLFragmentParser` is used.

    :type parser: :class:`xml.sax.xmlreader.XMLReader`
    '''
    def __init__(self, output=None, in_encoding='UTF-8', parser=None):
        if output is None:
            from ecoxipy.pyxom.output import PyXOMOutput
            output = PyXOMOutput()
        self._output = output
        self._in_encoding = in_encoding
        self._parser = parser

    def _prepare_text(self, content):
        try:
            return _unicode(content)
        except UnicodeDecodeError:
            return content.decode(self._in_encoding)

    def _preprocess(self, content, target_list, target_attributes=None,
            handle_text=None):
        if content is None:
            return
        if self._output.is_native_type(content):
            target_list.append(content)
            return
        if handle_text is None:
            handle_text = lambda text, target_list: target_list.append(
                self._output.text(text))
        if isinstance(content, bytes):
            content = self._prepare_text(content)
        if isinstance(content, _unicode):
            handle_text(content, target_list)
        elif (target_attributes is not None
                and isinstance(content, collections.Mapping)):
            for attr_name, attr_value in content.items():
                attr_name = self._prepare_text(attr_name)
                if attr_value is not None:
                    attr_value = self._prepare_text(attr_value)
                    target_attributes[attr_name] = attr_value
        elif isinstance(content,
                (collections.Sequence, collections.Iterable)):
            for value in content:
                self._preprocess(value, target_list, target_attributes,
                    handle_text)
        elif isinstance(content, collections.Callable):
            value = content()
            self._preprocess(value, target_list, target_attributes,
                handle_text)
        else:
            value = _unicode(content)
            handle_text(value, target_list)

    def _parse_xml_fragment(self, xml_fragment):
        try:
            xml_fragment_parser = self.__dict__['_v_xml_fragment_parser']
        except KeyError:
            from ecoxipy.parsing import XMLFragmentParser
            xml_fragment_parser = XMLFragmentParser(
                self._output, self._parser)
            self._v_xml_fragment_parser = xml_fragment_parser
        parsed = xml_fragment_parser.parse(xml_fragment)
        return parsed

    def _slice(self, key):
        if key.start is None: # Document
            doctype = key.stop
            if doctype is None:
                doctype_name = None
                doctype_publicid = None
                doctype_systemid = None
            elif isinstance(doctype, tuple):
                doctype_name, doctype_publicid, doctype_systemid = doctype
                if doctype_name is None:
                    raise ValueError(
                        'Doctype document element name (first element of tuple in slice end) must not be "None".')
                doctype_name = self._prepare_text(doctype_name)
                doctype_publicid = (
                    None if doctype_publicid is None
                    else self._prepare_text(doctype_publicid))
                doctype_systemid = (
                    None if doctype_systemid is None
                    else self._prepare_text(doctype_systemid))
            else:
                doctype_name = self._prepare_text(doctype)
                doctype_publicid = None
                doctype_systemid = None
            omit_xml_declaration = key.step is True
            if omit_xml_declaration or key.step is None:
                encoding = 'UTF-8'
            else:
                encoding = _unicode(key.step)
            def create_document(*children):
                new_children = []
                for child in children:
                    self._preprocess(child, new_children)
                return self._output.document(doctype_name,
                    doctype_publicid, doctype_systemid, new_children,
                    omit_xml_declaration, encoding)
            return create_document
        else: # Processing Instruction
            target = key.start
            if target is None:
                raise ValueError(
                    'Processing instruction target (slice start) must not be "None".')
            content = (None if key.stop is None
                else self._prepare_text(key.stop))
            return self._output.processing_instruction(target, content)

    def _item(self, key):
        key = self._prepare_text(key)
        def build(*children, **attributes):
            new_children = []
            new_attributes = {}
            for child in children:
                self._preprocess(child, new_children, new_attributes)
            for attr_name, value in attributes.items():
                new_attributes[_unicode(attr_name)] = self._prepare_text(value)
            return self._output.element(key, new_children, new_attributes)
        return build

    def __getattr__(self, name):
        '''\
        Return an
        :ref:`element-creating function <ecoxipy.MarkupBuilder.item_access>`.

        :param name: The element name.
        :returns: An element in the output representation.
        '''
        return self._item(name)

    def __getitem__(self, key):
        '''\
        Return an
        :ref:`element-creating function <ecoxipy.MarkupBuilder.item_access>`
        for item access or either a
        :ref:`processing instruction or a document <ecoxipy.MarkupBuilder.slicing>`
        for slicing.

        :param key: The element name or slicing values.
        :returns: An element, a processing instruction or a document in the
            output representation.
        '''
        if isinstance(key, slice):
            return self._slice(key)
        else:
            return self._item(key)

    def __call__(self, *content):
        '''
        Parses the ``content`` items as XML fragments, if they are not output
        representation objects. See :ref:`ecoxipy.MarkupBuilder.calling` for
        more information.

        :param content: The XML fragments to parse or objects of the output
            representation.
        :returns: Objects of the output representation.
        '''
        processed_content = []
        for content_element in content:
            self._preprocess(content_element, processed_content, None,
                lambda text, target_list: target_list.extend(
                    self._parse_xml_fragment(text))
            )
        return processed_content

    def __and__(self, content):
        '''\
        Creates a text node. See :ref:`ecoxipy.MarkupBuilder.operators` for
        more information.
        '''
        return self._output.text(self._prepare_text(content))

    def __or__(self, content):
        '''\
        Creates a comment. See :ref:`ecoxipy.MarkupBuilder.operators` for
        more information.
        '''
        return self._output.comment(self._prepare_text(content))


class Output(object):
    '''\
    Abstract base class defining the :class:`MarkupBuilder` output interface.

    The abstract methods are called by :class:`MarkupBuilder` instances to
    create XML representations. All data is assumed to be given as Unicode
    strings if not otherwise stated, :class:`MarkupBuilder` takes care of
    that.
    '''
    __metaclass__ = ABCMeta

    @abstractmethod
    def is_native_type(self, content):
        '''\
        Tests if an object of an type is to be decoded or converted to unicode
        or not.

        :param content: The object to test.
        :returns: :const:`True` for an object not to decode or convert to
            Unicode, :const:`False` otherwise.
        '''

    @abstractmethod
    def element(self, name, children, attributes):
        '''\
        Creates an element representation.

        :param name: The name of the element to create.
        :param children: The list of children to add to the element to
            create.
        :type children: :func:`list`
        :param attributes: The mapping of attributes of the element to create.
        :type attributes: :class:`dict`
        :returns: The element representation created.
        '''

    @abstractmethod
    def text(self, content):
        '''\
        Creates a text node representation.

        :param content: The text.
        :returns: The created text representation.
        '''

    @abstractmethod
    def comment(self, content):
        '''\
        Creates a comment representation.

        :param content: The content of the comment.
        :returns:
            The created comment representation.
        '''

    @abstractmethod
    def processing_instruction(self, target, content):
        '''\
        Creates a processing instruction representation.

        :param target: The target of the processing instruction.
        :param content: The content of the processing instruction.
        :returns:
            The created processing instruction representation.
        '''

    @abstractmethod
    def document(self, doctype_name, doctype_publicid, doctype_systemid,
            children, omit_xml_declaration, encoding):
        '''\
        Creates a XML document representation.

        :param doctype_name:  The document element name.
        :param doctype_publicid:  The document type system ID.
        :param doctype_systemid:  The document type system ID.
        :param children: The list of children to add to the document to
            create.
        :type children: :func:`list`
        :param omit_xml_declaration: If :const:`True` the XML declaration is
            omitted.
        :type omit_xml_declaration: :func:`bool`
        :type encoding: The encoding of the XML document.
        :returns:
            The created document representation.
        '''


class XMLWellFormednessException(Exception):
    '''\
    Indicates XML is not well-formed.

    This is used by :class:`ecoxipy.string_output.StringOutput` and
    :mod:`ecoxipy.pyxom`.
    '''


del ABCMeta, abstractmethod, sys
