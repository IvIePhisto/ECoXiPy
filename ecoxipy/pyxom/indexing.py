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

Indexer and Index Implementations
---------------------------------

.. autoclass:: ElementByUniqueAttributeValueIndexer

.. autoclass:: ElementsByNameIndexer

.. autoclass:: UniqueValueIndex

.. autoclass:: MultiValueIndex

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
    a specific key. Entries can be set using :meth:`register`.
    '''
    def __init__(self):
        self._index = {}

    def register(self, key, value):
        '''\
        Set the entry for ``key`` to ``value``.

        :param key: the identifier
        :param value: the entry's value
        :raises ValueError: if a value for ``key`` is already registered.
        '''
        if key in self._index:
            raise ValueError(
                u'A value for key "{}" is already registered'.format(key))
        self._index[key] = value

    def __getitem__(self, key):
        return self._index[key]

    def __contains__(self, key):
        return key in self._index

    def __len__(self):
        return len(self._index)

    def __iter__(self):
        return iter(self._index)

    def __repr__(self):
        return u'{}.{}{}'.format(self.__class__.__module__,
            self.__class__.__name__, repr(self._index))



class MultiValueIndex(UniqueValueIndex):
    '''\
    A read-only-semantics mapping holding a :class:`set` of values under a
    specific key. Values can be added to an key's set using :meth:`register`.
    '''
    def register(self, key, value):
        '''\
        Add ``value`` to the :class:`set` identified by ``key``. If no such
        set exists first a new one is created and registered under ``key``.

        :param key: the identifier
        :param value: the value to add to the entries :class:`set`
        '''
        try:
            values = self._index[key]
        except KeyError:
            values = set()
            UniqueValueIndex.register(self, key, values)
        values.add(value)

    def __getitem__(self, key):
        return (node for node in self._index[key])


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



del abc, collections