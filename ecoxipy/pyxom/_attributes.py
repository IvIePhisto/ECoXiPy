# -*- coding: utf-8 -*-
import abc
import collections

from ecoxipy import _unicode
from ecoxipy import _helpers

from ._common import _string_repr


class NamespaceNameMixin(object):
    '''\
    Contains functionality implementing `Namespaces in XML
    <http://www.w3.org/TR/REC-xml-names/>`_.
    '''
    __metaclass__ = abc.ABCMeta
    _namespace_name_slots__ = ('_namespace_prefix', '_local_name',
        '_v_namespace_uri', '_v_namespace_source')

    def _set_namespace_properties(self, index):
        components = _helpers.get_qualified_name_components(self.name)
        self._namespace_prefix, self._local_name = components
        return components[index]

    def _clear_namespace_uri(self):
        if hasattr(self, '_v_namespace_uri'):
            namespace_source = self._v_namespace_source
            if namespace_source is not None:
                namespace_source._remove_namespace_target(self)
            del self._v_namespace_uri
            del self._v_namespace_source

    def _clear_namespace_properties(self):
        self._clear_namespace_uri()
        del self._namespace_prefix
        del self._local_name

    @property
    def namespace_prefix(self):
        '''\
        The namespace prefix (the part before ``:``) of the node's name.
        '''
        try:
            return self._namespace_prefix
        except AttributeError:
            return self._set_namespace_properties(0)

    @property
    def local_name(self):
        '''\
        The local name (the part after ``:``) of the node's name.
        '''
        try:
            return self._local_name
        except AttributeError:
            return self._set_namespace_properties(1)

    @property
    def namespace_uri(self):
        '''\
        The namespace URI the :attr:`namespace_prefix` refers to. It is
        :const:`None` if there is no namespace prefix and it is :const:`False`
        if the prefix lookup failed.
        '''
        try:
            return self._v_namespace_uri
        except AttributeError:
            if self.parent is None:
                namespace_source = None
                namespace_uri = False
            else:
                if isinstance(self, Attribute):
                    if self.namespace_prefix is None:
                        namespace_source = None
                        namespace_uri = None
                    elif self.namespace_prefix == u'xml':
                        namespace_source = None
                        namespace_uri = u'http://www.w3.org/XML/1998/namespace'
                    elif self.namespace_prefix == u'xmlns':
                        namespace_source = None
                        namespace_uri = u'http://www.w3.org/2000/xmlns/'
                    else:
                        namespace_source = self.parent.parent
                else:
                    namespace_source = self
                if namespace_source is not None:
                    namespace_source, namespace_uri = namespace_source._get_namespace(
                        self.namespace_prefix)
                    if namespace_source is not None:
                        namespace_source._register_namespace_target(self)
            self._v_namespace_source = namespace_source
            self._v_namespace_uri = namespace_uri
            return namespace_uri


class Attribute(NamespaceNameMixin):
    '''\
    Represents an item of an :class:`Element`'s :class:`Attributes`. It
    inherits from :class:`NamespaceNameMixin` and should not be
    instantiated on itself, rather use :meth:`Attributes.create_attribute`.
    '''
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
            if self._check_well_formedness:
                if prefix == u'xmlns':
                    raise ecoxipy.XMLWellFormednessException(
                        u'The namespace prefix "xmlns" must not be redefined.'
                    )
                if prefix == u'xml':
                    raise ecoxipy.XMLWellFormednessException(
                        u'The namespace prefix "xml" must not be redefined.')
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
        '''\
        The attribute's name. On setting the value is converted to an
        Unicode string, if there is already another attribute with the
        same name on the :attr:`parent` :class:`Attributes` instance a
        :class:`KeyError` is raised.
        '''
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
        '''\
        The attribute's value.
        '''
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

    def __hash__(self):
        return object.__hash__(self)


class Attributes(collections.Mapping):
    '''\
    This mapping, containing :class:`Attribute` instances identified by their
    names, represents attributes of an :class:`Element`. It should not
    be instantiated on itself.
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
        '''\
        Create a new :class:`Attribute` as part of the instance.

        :param name: the attribute's name
        :param value: the attribute's value
        :returns: the created attribute
        :rtype: :class:`Attribute`
        :raises KeyError: If an attribute with ``name`` already exists in the
            instance.
        '''
        name = _unicode(name)
        if name in self._attributes:
            raise KeyError(
                u'An attribute with name "{}" already exists.'.format(name))
        value = _unicode(value)
        attribute = Attribute(self, name, value, self._check_well_formedness)
        self._attributes[name] = attribute
        return attribute

    def add(self, attribute):
        '''\
        Add an attribute to the instance. If the attribute is contained in an
        :class:`Attributes` instance it is first removed from that.

        :param attribute: the attribute to add
        :type attribute: :class:`Attribute`
        :raises ValueError: if attribute is no :class:`Attribute` instance
        :raises KeyError: If an attribute with the ``attribute``'s name
            already exists in the instance.
        '''
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
        '''\
        Remove the given ``attribute``.

        :param attribute: the attribute to remove
        :type attribute: :class:`Attribute`
        :raises KeyError: If no attribute with the name of ``attribute``
            is contained in the instance.
        :raises ValueError: If there is an attribute with the name of
            ``attribute`` contained, but it is not ``attribute``.
        '''
        self_attribute = self._attributes[attribute.name]
        if self_attribute is not attribute:
            raise KeyError(
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
        '''\
        Creates a :class:`dict` from the instance's :class:`Attribute`
        instances. The keys are the attribute's names, identifying the
        attribute's values.
        '''
        return {
            attribute.name: attribute.value
            for attribute in self.values()
        }

    def __hash__(self):
        return object.__hash__(self)


del abc, collections
