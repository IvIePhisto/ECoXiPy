# -*- coding: utf-8 -*-
'''\

:mod:`ecoxipy` - The ECoXiPy API
================================

The package :mod:`ecoxipy` provides the basic API, consisting of
:class:`MarkupBuilder` and :class:`Output`.
'''

import collections
from abc import ABCMeta, abstractmethod


class MarkupBuilder(object):
    ur'''\
    A builder for creating XML in a pythonic way.

    :param output:

        The output to use. If this is :const:`None`,
        :class:`ecoxipy.element_output.ElementOutput` is used.

    :type output: :class:`Output`


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
            identified by the key. The keys and values should be :func:`str`
            or :func:`unicode` instances.

        Those items of ``children``, which are iterable mapping types
        (``child[name] for name in child``) define attributes. The entries of
        ``attributes`` overwrite entries from ``children`` items.

        Those other items of ``children``, which are iterable or iterators
        are replaced with their items, callables are replaced with the
        result of their call.


    As this way not all element names can be used, you can retrieve a
    building method using the subscript syntax. If such a method is given as a
    child, it is called while building. This way creating elements without
    children or attributes is shorter.

    You can also call :class:`MarkupBuilder` instances. As with the
    ``children`` argument of the builder's dynamic methods, those elements of
    the argument list, which are iterable or iterators, are unpacked. Those
    arguments which are callables are replaced by the result of the call. The
    :class:`MarkupBuilder` instance call returns an
    :class:`Output`-implementation-dependant representation for the list
    of arguments. In this process the arguments are parsed, converted,
    encoded or kept the same, depending on their type and the
    :class:`Output` implementation.

    You can create processing instructions using the slicing operator with a
    start argument, which becomes the target. If the end argument is specified
    it becomes the content. So the slice `['xml-stylesheet',
    'href="style.css"']` becomes a processing instruction with target
    `xml-stylesheet` and content `href="style.css"`.

    If the slicing start argument is not specified, a function creating a XML
    document is returned. The arguments of that function become the document
    root nodes. The slicing end argument (if specified) denotes the document
    type declaration content. It can either be the document element name as a
    :func:`str` or :func:`unicode` or a 3-:func:`tuple` containing the
    document element name, the public ID and the system ID. The slicing step
    argument (if specified) defines if the XML declaration should be omitted,
    it defaults to :const:`False` (this may not be honoured by :class:`Output`
    implementations).

    The following operators create special nodes from their argument:

    `&`
        Creates a text node.

    `|`
        Creates a comment.
    '''
    def __init__(self, output=None):
        if output is None:
            from element_output import ElementOutput
            output = ElementOutput()
        self._output = output

    @classmethod
    def _preprocess(cls, content, target_list, target_attributes=None):
        if content is None:
            return
        if isinstance(content, (str, unicode)):
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
        return self._output.embed(processed_content)

    def __getitem__(self, name):
        if isinstance(name, slice):
            if name.start is None:
                doctype = name.stop
                if isinstance(doctype, tuple):
                    doctype_name, doctype_publicid, doctype_systemid = doctype
                else:
                    doctype_name = doctype
                    doctype_publicid = None
                    doctype_systemid = None
                omit_xml_declaration = name.step
                if omit_xml_declaration is None:
                    omit_xml_declaration = False
                def create_document(*children):
                    new_children = []
                    for child in children:
                        self._preprocess(child, new_children)
                    return self._output.document(doctype_name,
                        doctype_publicid, doctype_systemid, new_children,
                        omit_xml_declaration)
                return create_document
            else:
                target = name.start
                content = name.stop
                if content is None:
                    content = ''
                return self._output.processing_instruction(target, content)
        def build(*children, **attributes):
            new_children = []
            new_attributes = {}
            for child in children:
                self._preprocess(child, new_children, new_attributes)
            for attr_name in attributes:
                new_attributes[attr_name] = attributes[attr_name]
            return self._output.element(name, new_children, new_attributes)
        return build

    __getattr__ = __getitem__

    def __and__(self, content):
        processed_content = []
        self._preprocess(content, processed_content)
        return self._output.text(processed_content)

    def __or__(self, content):
        return self._output.comment(content)


class Output(object):
    '''\
    Abstract base class defining the :class:`MarkupBuilder` output interface.

    The abstract methods are called by :class:`MarkupBuilder` instances to
    create an element (:meth:`element`) or to add raw data (:meth:`embed`).
    '''
    __metaclass__ = ABCMeta

    @abstractmethod
    def element(self, name, children, attributes):
        '''\
        Abstract method, override in implementation class. This is called by
        :class:`MarkupBuilder` instances.

        :param name: The name of the element to create.
        :type name: :func:`str` or :func:`unicode`
        :param children: The list of children to add to the element to
            create.
        :type children: :func:`list`
        :param attributes: The mapping of attributes of the element to create.
        :type attributes: :class:`dict`
        :returns: The element representation created.
        '''

    @abstractmethod
    def embed(self, content):
        '''\
        Imports the elements of ``content`` as data in the output
        representation.

        :param content: The list of data to parse.
        :type content: :func:`list`
        :returns:
            A list of child representations or a single child representation.
        '''

    @abstractmethod
    def text(self, content):
        '''\
        Creates text node representations.

        :param content: The list of texts.
        :type content: :func:`list`
        :returns:
            A list of text representations or a single text representation.
        '''

    @abstractmethod
    def comment(self, content):
        '''\
        Creates a comment node representation.

        :param content: The content of the comment.
        :type content: :func:`str` or :func:`unicode`
        :returns:
            The created comment representation.
        '''

    @abstractmethod
    def processing_instruction(self, target, content):
        '''\
        Creates a processing instruction node representation.

        :param target: The target of the processing instruction.
        :type target: :func:`str` or :func:`unicode`
        :param content: The content of the processing instruction.
        :type content: :func:`str`, :func:`unicode` or const:`None`
        :returns:
            The created processing instruction representation.
        '''

    @abstractmethod
    def document(self, doctype_name, doctype_publicid, doctype_systemid,
            children, omit_xml_declaration):
        '''\
        Creates a XML document representation.

        :param doctype_name:  The document element name.
        :type doctype_name: :func:`str`, :func:`unicode`, :const:`None`
        :param doctype_publicid:  The document type system ID.
        :type doctype_publicid: :func:`str`, :func:`unicode`, :const:`None`
        :param doctype_systemid:  The document type system ID.
        :type doctype_systemid: :func:`str`, :func:`unicode`, :const:`None`
        :param children: The list of children to add to the document to
            create.
        :type children: :func:`list`
        :param omit_xml_declaration: If :const:`True` the XML declaration is
            omitted.
        :type omit_xml_declaration: :func:`bool`
        :returns:
            The created document representation.
        '''

del ABCMeta
del abstractmethod
