# -*- coding: utf-8 -*-
'''\

:mod:`ecoxipy` - The ECoXiPy API
================================

The package :mod:`ecoxipy` provides the basic API, consisting of
:class:`MarkupBuilder` and :class:`Output`.
'''

import sys
import collections
import xml.sax.xmlreader
from abc import ABCMeta, abstractmethod

_python3 = sys.version_info[0] >= 3
_unicode = str if _python3 else unicode

import ecoxipy.parsing



class MarkupBuilder(object):
    u'''\
    A builder for creating XML in a pythonic way. All byte strings given are
    are decoded with the input encoding specified on instanciation.

    :param output:

        The output to use. If this is :const:`None`,
        :class:`ecoxipy.element_output.ElementOutput` is used.

    :type output: :class:`Output`

    :param in_encoding:

        The input encoding to be used to decode byte strings to Unicode.


    **Attributes and Item Retrieval - Elements**

    Each attribute access on an instance of this class returns a method, which
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


    As this way not all element names can be used, you can retrieve a
    building method using the subscript syntax. If such a method is given as a
    child, it is called while building. This way creating elements without
    children or attributes is shorter.


    **Calling - XML Fragments**

    You can also call :class:`MarkupBuilder` instances to parse XML fragments
    (lists of XML Nodes). As with the ``children`` argument of the builder's
    dynamic methods, the arguments are unpacked and converted to Unicode, but
    here each of the Unicode strings is parsed as XML using
    :`ecoxipy.parsing.XMLFragmentParser`. This will raise a
    :class:`xml.sax.SAXException` if the XML is not well-formed.


    **Slicing - Processing Instructions and Documents**

    You can create processing instructions by using the slicing operator with
    a start argument, which becomes the target. If the end argument is
    specified it becomes the content. So the slice `['xml-stylesheet',
    'href="style.css"']` becomes a processing instruction with target
    `xml-stylesheet` and content `href="style.css"`.

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
    omitted.


    **Operators - Text and Comments**

    The following operators create special nodes from their argument:

    ``&``
        Creates a text node.

    ``|``
        Creates a comment.
    '''
    def __init__(self, output=None, in_encoding='UTF-8'):
        if output is None:
            from ecoxipy.element_output import ElementOutput
            output = ElementOutput()
        self._output = output
        self._in_encoding = in_encoding

    @property
    def in_encoding(self):
        '''\
        The input encoding to be used to decode byte strings to Unicode.
        '''
        return self._in_encoding

    def _prepare_text(self, content):
        try:
            return _unicode(content)
        except UnicodeDecodeError:
            return content.decode(self._in_encoding)

    def _preprocess(self, content, target_list, target_attributes=None):
        if content is None:
            return
        if (self._output.is_native_type(content)
                or isinstance(content, _unicode)):
            target_list.append(content)
        elif isinstance(content, bytes):
            value = self._prepare_text(content)
            target_list.append(value)
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
                self._preprocess(value, target_list, target_attributes)
        elif isinstance(content, collections.Callable):
            value = content()
            self._preprocess(value, target_list, target_attributes)
        else:
            value = _unicode(content)
            target_list.append(value)

    def _parse_xml_fragment(self, xml_fragment):
        try:
            xml_fragment_parser = self.__dict__['_v_xml_fragment_parser']
        except KeyError:
            xml_fragment_parser = ecoxipy.parsing.XMLFragmentParser(
                self._output)
            self._v_xml_fragment_parser = xml_fragment_parser
        parsed = xml_fragment_parser.parse(xml_fragment)
        return parsed

    def __call__(self, *content):
        processed_content = []
        for content_element in content:
            self._preprocess(content_element, processed_content)
        parsed_content = []
        for content_element in processed_content:
            if isinstance(content_element, _unicode):
                parsed_content.extend(self._parse_xml_fragment(
                    content_element))
            else:
                parsed_content.append(content_element)
        return parsed_content

    def __getitem__(self, name):
        if isinstance(name, slice):
            if name.start is None: # Document
                doctype = name.stop
                if doctype is None:
                    raise ValueError(
                        'Doctype (slice end) must not be "None".')
                if isinstance(doctype, tuple):
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
                omit_xml_declaration = name.step is True
                if omit_xml_declaration or name.step is None:
                    encoding = 'UTF-8'
                else:
                    encoding = _unicode(name.step)
                def create_document(*children):
                    new_children = []
                    for child in children:
                        self._preprocess(child, new_children)
                    return self._output.document(doctype_name,
                        doctype_publicid, doctype_systemid, new_children,
                        omit_xml_declaration, encoding)
                return create_document
            else: # Processing Instruction
                target = name.start
                if target is None:
                    raise ValueError(
                        'Processing instruction target (slice start) must not be "None".')
                content = (None if name.stop is None
                    else self._prepare_text(name.stop))
                return self._output.processing_instruction(target, content)
        else:
            name = self._prepare_text(name)
        def build(*children, **attributes):
            new_children = []
            new_attributes = {}
            for child in children:
                self._preprocess(child, new_children, new_attributes)
            for attr_name, value in attributes.items():
                new_attributes[_unicode(attr_name)] = self._prepare_text(value)
            return self._output.element(name, new_children, new_attributes)
        return build

    __getattr__ = __getitem__

    def __and__(self, content):
        return self._output.text(self._prepare_text(content))

    def __or__(self, content):
        return self._output.comment(self._prepare_text(content))


class Output(object):
    '''\
    Abstract base class defining the :class:`MarkupBuilder` output interface.

    The abstract methods are called by :class:`MarkupBuilder` instances to
    create an element (:meth:`element`) or to add raw data (:meth:`embed`).

    All data is assumed to be given as Unicode strings, :class:`MarkupBuilder`
    takes care of that.
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
        Abstract method, override in implementation class. This is called by
        :class:`MarkupBuilder` instances.

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
        Creates a comment node representation.

        :param content: The content of the comment.
        :returns:
            The created comment representation.
        '''

    @abstractmethod
    def processing_instruction(self, target, content):
        '''\
        Creates a processing instruction node representation.

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


del ABCMeta, abstractmethod, sys
