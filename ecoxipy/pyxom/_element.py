# -*- coding: utf-8 -*-
import collections
from xml.sax.xmlreader import AttributesImpl

from ecoxipy import _python2, _unicode
from ecoxipy import _helpers

from ._common import XMLNode, ContainerNode, _string_repr
from ._attributes import NamespaceNameMixin, Attributes
from ._content_nodes import Text


class Element(ContainerNode, NamespaceNameMixin):
    '''\
    Represents a XML element. It inherits from :class:`ContainerNode` and
    :class:`NamespaceNameMixin`.

    :param name: The name of the element to create.
    :type name: Unicode string
    :param children: The children :class:`XMLNode` instances of the element.
    :type children: iterable of items
    :param attributes: Defines the attributes of the element. Must be usable
        as the parameter of :class:`dict` and should contain only Unicode
        strings as key and value definitions.
    :param check_well_formedness: If :const:`True` the element name and
        attribute names will be checked to be a valid XML name.
    :type check_well_formedness: :func:`bool`
    :raises ecoxipy.XMLWellFormednessException: If
        ``check_well_formedness`` is :const:`True` and the
        ``name`` is not a valid XML name.
    '''
    __slots__ = NamespaceNameMixin._namespace_name_slots__ + (
        '_name', '_attributes',  '_namespace_prefix_to_uri',
        '_namespace_targets', '_namespace_prefix_to_target')

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
            have a method :meth:`items()` (like :class:`dict`) which returns
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
        '''\
        An iterator over all namespace prefixes defined in the element and
        its parents. Duplicate values may be retrieved.
        '''
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
        '''\
        Calculates the element the namespace ``prefix`` is defined in, this
        is :const:`None` if the prefix is not defined.
        '''
        return self._get_namespace(prefix)[0]

    def get_namespace_uri(self, prefix):
        '''\
        Calculates the namespace URI for the ``prefix``, this is
        :const:`False` if the prefix is not defined..
        '''
        return self._get_namespace(prefix)[1]

    @property
    def name(self):
        '''\
        The name of the element. On setting the value is converted to an
        Unicode string; a :class:`ecoxipy.XMLWellFormednessException` is
        thrown if it is not a valid XML name and ``check_well_formedness``
        is :const:`True`.
        '''
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

    def __hash__(self):
        return object.__hash__(self)

    @_helpers.inherit_docstring(ContainerNode)
    def duplicate(self):
        return Element(self._name,
            [child.duplicate() for child in self],
            self._attributes.to_dict())

del collections
