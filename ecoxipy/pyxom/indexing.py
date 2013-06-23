'''\
:mod:`ecoxipy.pyxom.indexing` - Indexing PyXOM Structures
=========================================================

This package is a foundation for indexing :mod:`ecoxipy.pyxom` structures.
The abstract base class :class:`Indexer` establishes an interface for indexing
PyXOM structures.


Two mapping implementations are provided to serve as indexes:

*   :class:`UniqueValueIndex` allows only one value per key.

*   :class:`MultiValueIndex` holds a :class:`set` of values per key.


For easier implementation of indexers there are some abstract base classes:

*   :meth:`Indexer.new_index` and :meth:`Indexer.register` are implemented by
    :class:`UniqueValueIndexer` and :class:`MultiValueIndexer`, which use
    :class:`UniqueValueIndex` or :class:`MultiValueIndex` respectively.

*   :class:`AttributeValueIndexer` in contrast implements
    :meth:`Indexer.node_predicate` and :meth:`Indexer.extract_items` to index
    attributes by their value.


Two ready-to-use indexer implementations are provided:

*   :class:`ElementByUniqueAttributeValueIndexer` indexes
    :class:`ecoxipy.pyxom.Element` instances under the value of a specific
    attribute they have, e.g. ``xml:id`` or ``id``.

*   To index :class:`ecoxipy.pyxom.Element` instances by their name use
    :class:`ElementsByNameIndexer`.


The :class:`IndexDescriptor` makes index access and deletion more convenient.


.. _ecoxipy.pyxom.indexing.examples:

Examples
--------

First we create a test document:

>>> from ecoxipy import MarkupBuilder
>>> b = MarkupBuilder()
>>> test = b.test(
...     b.foo(id='b'),
...     b.foo('Foo Bar', no_id='d'),
...     b.bar(id='c'),
...     id='a'
... )


Here is an example how to use :class:`ElementByUniqueAttributeValueIndexer`:

>>> indexer = ElementByUniqueAttributeValueIndexer()
>>> index = indexer(test)
>>> len(index) == 3
True
>>> u'a' in index and index[u'a'] is test
True
>>> index[u'b'] is test[0] and index[u'c'] is test[-1]
True
>>> u'd' in index
False
>>> index = indexer(b[:](b.test0(id='test'), b.test1(id='test')))
Traceback (most recent call last):
ValueError: A value for key "test" is already registered

And this is how :class:`ElementsByNameIndexer` works:

>>> indexer = ElementsByNameIndexer()
>>> index = indexer(test)
>>> len(index) == 3
True
>>> u'test' in index
True
>>> list(index[u'test'])[0] is test
True
>>> u'bar' in index
True
>>> list(index[u'bar'])[0] is test[-1]
True
>>> foo_elements = set(index[u'foo'])
>>> len(foo_elements) == 2
True
>>> foo_elements == {test[0], test[1]}
True
>>> u'unknown' in index
False



.. _ecoxipy.pyxom.indexing.abc:

Abstract Base Classes
---------------------

.. autoclass:: Indexer
    :special-members: __call__

.. autoclass:: UniqueValueIndexer

.. autoclass:: MultiValueIndexer

.. autoclass:: AttributeValueIndexer



.. _ecoxipy.pyxom.indexing.implementations:

Indexing-related Classes
------------------------

.. autoclass:: ElementByUniqueAttributeValueIndexer

.. autoclass:: ElementsByNameIndexer

.. autoclass:: UniqueValueIndex

.. autoclass:: MultiValueIndex

.. autoclass:: NamespaceIndex

.. autoclass:: NamespaceIndexer
    :special-members: __call__

.. autoclass:: IndexDescriptor
'''

import abc
import collections

from collections import Iterator as _Iterator

from ecoxipy import _unicode


class Indexer(object):
    '''\
    Abstract base class for :mod:`ecoxipy.pyxom` stucture indexers.
    '''
    __metaclass__ = abc.ABCMeta

    def __call__(self, root_node):
        '''\
        Indexes a :class:`ecoxipy.pyxom.XMLNode` tree.

        :param root_node: the node to start indexing on
        :type root_node: :class:`ecoxipy.pyxom.ContainerNode`
        :returns: an index data structure

        The following is done for indexing:

        1.  :meth:`new_index` is called to create the index data structure.

        2.  For ``root_node`` and its descendants on which
            :meth:`node_predicate` returns :const:`True`:

            1.  A single item or an iterator of items is obtained by calling
                :meth:`extract_items`.

            2.  The single item or each item of the iterator is registered on
                the index by calling :meth:`register`.

        3.  The index data structure ist returned.
        '''
        index = self.new_index()
        def register(node):
            items = self.extract_items(node)
            if isinstance(items, _Iterator):
                for key, node in items:
                    self.register(index, key, node)
            else:
                key, node = items
                self.register(index, key, node)
        if self.node_predicate(root_node):
            register(root_node)
        for node in filter(self.node_predicate, root_node.descendants()):
            register(node)
        return index

    @abc.abstractmethod
    def new_index(self):
        '''\
        Creates and returns an index data structure.
        '''
        pass

    @abc.abstractmethod
    def node_predicate(self, node):
        '''\
        Determines if ``node`` should be used to extract index items from.

        :param node: the node to test
        :type node: :class:`ecoxipy.pyxom.XMLNode`
        :returns: :const:`True` if ``node`` should be used to extract index
            items, :const:`False` otherwise.
        '''
        pass

    @abc.abstractmethod
    def extract_items(self, node):
        '''\
        Extracts index items from ``node``. An index item is a 2-:func:`tuple`
        with the key as first item and value as second item.

        :param node: the node to extract index items from
        :type node: :class:`ecoxipy.pyxom.XMLNode`
        :returns: A single index item or an iterator of index items.
        '''
        pass

    @abc.abstractmethod
    def register(self, index, key, value):
        '''\
        Registers ``value`` under ``key`` on ``index``.

        :param index: the index data structure
        :param key: the identifier for ``value``
        :param value: the value registered under ``key``
        '''
        pass


class UniqueValueIndex(collections.Mapping):
    '''\
    A read-only-semantics mapping enforcing only one value is registered under
    a specific key. Entries can be set using :meth:`register`. Value access
    and containment tests convert the key to a Unicode string first.
    '''
    def __init__(self):
        self._index = {}

    def register(self, key, value):
        '''\
        Set the entry for ``key`` to ``value``.

        :param key: the identifier
        :type key: Unicode string
        :param value: the entry's value
        :raises ValueError: if a value for ``key`` is already registered.
        '''
        if key in self._index:
            raise ValueError(
                u'A value for key "{}" is already registered'.format(key))
        self._index[key] = value

    def __getitem__(self, key):
        key = _unicode(key)
        return self._index[key]

    def __contains__(self, key):
        key = _unicode(key)
        return key in self._index

    def __len__(self):
        return len(self._index)

    def __iter__(self):
        return iter(self._index)

    def __repr__(self):
        return u'{}.{}{}'.format(self.__class__.__module__,
            self.__class__.__name__, repr(self._index))


class _MultiDict(dict):
    def __setitem__(self, key, value):
        try:
            values = dict.__getitem__(self, key)
        except KeyError:
            values = set()
            dict.__setitem__(self, key, values)
        values.add(value)

    def __getitem__(self, key):
        return (value for value in dict.__getitem__(self, key))

    def __call__(self, key):
        return dict.__getitem__(self, key)


class MultiValueIndex(UniqueValueIndex):
    '''\
    A read-only-semantics mapping holding a :class:`set` of values under a
    specific key. Values can be added to an key's set using :meth:`register`.
    Value access and containment tests convert the key to a Unicode string
    first.
    '''
    def __init__(self):
        self._index = _MultiDict()

    def register(self, key, value):
        '''\
        Add ``value`` to the set identified by ``key``.

        :param key: the identifier
        :type key: Unicode string
        :param value: the entry's value
        '''
        key = _unicode(key)
        self._index[key] = value


class UniqueValueIndexer(Indexer):
    '''\
    An abstract :class:`Indexer` base class which uses
    :class:`UniqueValueIndex` as the index.
    '''
    def new_index(self):
        '''\
        Creates and returns an :class:`UniqueValueIndex` instance.
        '''
        return UniqueValueIndex()

    def register(self, index, key, node):
        '''\
        Registers ``value`` under ``key`` by calling ``register(key, value)``
        on ``index``.
        '''
        index.register(key, node)


class MultiValueIndexer(UniqueValueIndexer):
    '''\
    An abstract :class:`Indexer` base class which uses
    :class:`MultiValueIndex` as the index.
    '''
    def new_index(self):
        '''\
        Creates and returns a :class:`MultiValueIndex` instance.
        '''
        return MultiValueIndex()


class AttributeValueIndexer(Indexer):
    '''\
    An abstract :class:`Indexer` base class which selects
    :class:`ecoxipy.pyxom.Element` nodes that contain an
    :class:`ecoxipy.pyxom.Attribute` having a name equal to
    ``attribute_name``. The index items are those attributes, identified by
    their value.

    :param attribute_name: defines :attr:`attribute_name`
    '''
    def __init__(self, attribute_name):
        self._attribute_name = attribute_name
        from ._element import Element
        self._node_class = Element

    @property
    def attribute_name(self):
        '''\
        The name of the attributes whose values define the indexing keys.
        '''
        return self._attribute_name

    def node_predicate(self, node):
        '''\
        Returns :const:`True` if ``node`` is an :class:`ecoxipy.pyxom.Element`
        instance and has an attribute with name :attr:`attribute_name`,
        :const:`False` otherwise.
        '''
        return (isinstance(node, self._node_class)
            and self._attribute_name in node.attributes)

    def extract_items(self, node):
        '''\
        Returns a 2-:func:`tuple` with the value of the attribute with name
        :attr:`attribute_name` on ``node`` as first item and the attribute
        itself as second item.
        '''
        attribute = node.attributes[self._attribute_name]
        return (attribute.value, attribute)


class ElementByUniqueAttributeValueIndexer(UniqueValueIndexer,
        AttributeValueIndexer):
    '''\
    An :class:`Indexer` implementation creating an :class:`UniqueValueIndex`
    of elements having an attribute with the name equal to ``attribute_name``
    identified by the value of that attribute.

    :param attribute_name: defines
        :attr:`AttributeValueIndexer.attribute_name`
    '''
    def __init__(self, attribute_name=u'id'):
        AttributeValueIndexer.__init__(self, attribute_name)

    def extract_items(self, node):
        '''\
        Returns a 2-:func:`tuple` with the value of the attribute with name
        :attr:`AttributeValueIndexer.attribute_name` on ``node`` as first item
        and ``node`` as second item.
        '''
        attribute = node.attributes[self._attribute_name]
        return (attribute.value, node)


class ElementsByNameIndexer(MultiValueIndexer):
    '''\
    An :class:`Indexer` implementation creating an :class:`MultiValueIndex`
    of elements identified by their name.
    '''
    def __init__(self):
        from ._element import Element
        self._node_class = Element

    def node_predicate(self, node):
        '''\
        Returns :const:`True` if ``node`` is an :class:`ecoxipy.pyxom.Element`
        instance, :const:`False` otherwise.
        '''
        return isinstance(node, self._node_class)

    def extract_items(self, node):
        '''\
        Returns a 2-:func:`tuple` with the name of ``node`` as first item
        and ``node`` as second item.
        '''
        return (node.name, node)


class NamespaceIndex(object):
    '''\
    An index holding XML namespace information.

    Nodes are retrieved by calling an instance.
    '''
    def __init__(self):
        self._by_namespace_uri = _MultiDict()
        self._by_local_name = _MultiDict()

    def register(self, namespace_uri, local_name, node):
        '''\
        Registers the node with the namespace information.

        :param namespace_uri: The namespace URI of the node.
        :param local_name: The local name of the node.
        :param node: The node to register.
        '''
        self._by_namespace_uri[namespace_uri] = node
        self._by_local_name[local_name] = node

    def __call__(self, uri=True, local_name=True):
        '''\
        Retrieve an iterator over the nodes with the namespace information
        specified by the arguments.

        :param uri: The namespace URI to match. If this is :const:`True` all
            nodes with a
            :attr:`~ecoxipy.pyxom.NamespaceNameMixin.namespace_uri` different
            from :const:`False` (i.e. invalid namespace information) will
            be matched. Otherwise only those nodes with a namespace URI equal
            to this value will be matched.
        :param local_name: The local name to match. If this is :const:`True`
            the :attr:`~ecoxipy.pyxom.NamespaceNameMixin.local_name` value is
            not taken into account. Otherwise those nodes with the local name
            equal to this value will be matched.
        :raises KeyError: If either a non-:const:`True` ``uri`` or
            ``local_name`` cannot be found.
        '''
        if uri is not True and uri is not False:
            uri = _unicode(uri)
        if local_name is not True:
            local_name = _unicode(local_name)
        def all():
            for namespace_uri in self._by_namespace_uri:
                if namespace_uri is not False:
                    for node in self._by_namespace_uri[namespace_uri]:
                        yield node
        if uri is True:
            if local_name is True:
                return all()
            return self._by_local_name[local_name]
        if local_name is True:
            return self._by_namespace_uri[uri]
        return iter(self._by_namespace_uri(uri).intersection(
            self._by_local_name(local_name)))


class NamespaceIndexer(Indexer):
    def __init__(self):
        from ._element import Element
        self._node_class = Element

    def new_index(self):
        return NamespaceIndex()

    def node_predicate(self, node):
        return isinstance(node, self._node_class)

    def extract_items(self, node):
        create_item = lambda node: ((node.namespace_uri, node.local_name),
            node)
        def iterator():
            yield create_item(node)
            for attribute in node.attributes.values():
                yield create_item(attribute)
        return iterator()

    def register(self, index, key, value):
        namespace_uri, local_name = key
        index.register(namespace_uri, local_name, value)


class IndexDescriptor(object):
    '''\
    A descriptor handling index creation using a given :class:`Indexer`.

    :param indexer: The indexer to use for indexing, this becomes
        :attr:`indexer`.
    :type indexer: :class:`Indexer`.

    On value retrieval this descriptor returns itself on classes, on instances
    it returns an index created by the indexer. If such does not yet exist,
    first a new one is created.

    Attribute setting is not allowed by the descriptor. Deletion deletes the
    index for the instance.

    **Important:** This class does not hold track of changes in the indexed
    structures for performance reasons. It is the responsibility of using
    code to ensure the index is deleted after an instance is modified.

    This descriptor does not modify the indexed instance, instead it holds a
    :class:`weakref.WeakValueDictionary`, mapping instance IDs (as generated
    by :func:`id`) to the generated index for the instance.
    '''
    def __init__(self, indexer):
        self._indexer = indexer
        from weakref import WeakValueDictionary
        self._indexes = WeakValueDictionary()

    @property
    def indexer(self):
        '''\
        The :class:`Indexer` instance used for index creation.
        '''
        return self._indexer

    def __get__(self, instance, owner):
        if instance is None:
            return self
        instance_id = id(instance)
        try:
            index = self._indexes[instance_id]
        except KeyError:
            index = self._indexer(instance)
            self._indexes[instance_id] = index
        return index

    def __set__(self, instance, value):
        raise AttributeError('No setting allowed.')

    def __delete__(self, instance):
        instance_id = id(instance)
        try:
            del self._indexes[instance_id]
        except KeyError:
            pass

del abc, collections