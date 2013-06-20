# -*- coding: utf-8 -*-

import abc
import collections
from xml.sax.xmlreader import AttributesImpl
from xml.sax.saxutils import XMLGenerator

from ecoxipy import _python2, _unicode
from ecoxipy.string_output import StringOutput
from ecoxipy import _helpers


_string_repr = lambda value: 'None' if value is None else "'{}'".format(
    value.encode('unicode_escape').decode().replace("'", "\\'"))


class XMLNode(object):
    '''\
    Base class for XML node objects.

    Retrieving the byte string from an instance yields a byte string encoded
    as `UTF-8`.
    '''
    __metaclass__ = abc.ABCMeta
    __slots__ = ('_parent', '_next', '_previous')

    _string_output = StringOutput()

    def _attribute_node(self, attribute):
        try:
            return getattr(self, attribute)
        except AttributeError:
            return None

    @property
    def parent(self):
        '''\
        The parent :class:`ContainerNode` or :const:`None` if the node has no
        parent.
        '''
        return self._attribute_node('_parent')

    @property
    def previous(self):
        '''\
        The previous :class:`XMLNode` or :const:`None` if the node has no
        preceding sibling.
        '''
        return self._attribute_node('_previous')

    @property
    def next(self):
        '''\
        The next :class:`XMLNode` or :const:`None` if the node has no
        following sibling.
        '''
        return self._attribute_node('_next')

    def _attribute_iterator(self, attribute):
        def iterator(current):
            while True:
                current = current._attribute_node(attribute)
                if current is None:
                    break
                else:
                    yield current
        return iterator(self)

    @property
    def ancestors(self):
        '''\
        Returns an iterator over all ancestors.
        '''
        return self._attribute_iterator('_parent')

    @property
    def preceding_siblings(self):
        '''\
        Returns an iterator over all preceding siblings.
        '''
        return self._attribute_iterator('_previous')

    @property
    def following_siblings(self):
        '''\
        Returns an iterator over all following siblings.
        '''
        return self._attribute_iterator('_next')

    def _attribute_climbing_iterator(self, attribute):
        nodes = list(self._attribute_iterator(attribute))
        while nodes:
            current = nodes.pop(0)
            yield current
            if len(nodes) == 0:
                parent = current.parent
                if parent is not None:
                    nodes.extend(parent._attribute_iterator(attribute))

    @property
    def preceding(self):
        '''\
        Returns an iterator over all preceding nodes.
        '''
        return self._attribute_climbing_iterator('_previous')

    @property
    def following(self):
        '''\
        Returns an iterator over all following nodes.
        '''
        return self._attribute_climbing_iterator('_next')

    def create_str(self, out=None, encoding='UTF-8'):
        '''\
        Creates a string containing the XML representation of the node.

        :param out: A :class:`ecoxipy.string_output.StringOutput` instance or
            :const:`None`. If it is the latter, a new
            :class:`ecoxipy.string_output.StringOutput` instance is created.
        :param encoding: The output encoding or :const:`None` for Unicode
            output. Is only taken into account if ``out`` is :const:`None`.
        '''
        if out is None:
            out = self._string_output
        output_string = self._create_str(out)
        if encoding is not None:
            output_string = output_string.encode(encoding)
        return output_string

    def create_sax_events(self, content_handler=None, out=None,
            out_encoding='UTF-8', indent_incr=None):
        '''\
        Creates SAX events.

        :param content_handler: If this is :const:`None` a
            :class:`xml.sax.saxutils.XMLGenerator` is created and used as the
            content handler. If in this case ``out`` is not :const:`None`,
            it is used for output.
        :type content_handler: :class:`xml.sax.ContentHandler`
        :param out: The output to write to if no ``content_handler`` is given.
            It should have a :meth:`write` method like files.
        :param out_encoding: The output encoding or :const:`None` for
            Unicode output.
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
            indent_incr = _unicode(indent_incr)
            indent = (indent_incr, 0)
        self._create_sax_events(content_handler, indent)
        return content_handler

    def __str__(self):
        return _unicode(self.create_str(encoding=None))

    def __bytes__(self):
        return self.create_str(encoding='UTF-8')

    if _python2:
        __unicode__ = __str__
        __str__ = __bytes__
        del __bytes__

    def __hash__(self):
        return object.__hash__(self)

    @abc.abstractmethod
    def duplicate(self, test=None):
        '''\
        Return a deep copy of the XML node, and its descendants if it is a
        :class:`ContainerNode` instance.
        '''

    @abc.abstractmethod
    def _create_str(self, out):
        pass

    @abc.abstractmethod
    def _create_sax_events(self, content_handler, indent):
        pass

    @abc.abstractmethod
    def __repr__(self):
        pass

    @abc.abstractmethod
    def __eq__(self, other):
        pass

    @abc.abstractmethod
    def __ne__(self, other):
        pass


class ContainerNode(XMLNode, collections.MutableSequence):
    '''\
    A :class:`XMLNode` containing other nodes with sequence semantics.

    :param children: The nodes contained of in the node.
    :type children: :func:`list`
    '''
    __metaclass__ = abc.ABCMeta
    __slots__ = ('_children')

    def __init__(self, children):
        self._children = children
        for i, child in enumerate(children):
            child._parent = self
            if i > 0:
                self._wire_neighbors(previous, child)
            previous = child

    def children(self, reverse=False):
        '''\
        Returns an iterator over the children.

        :param reverse: If this is :const:`True` the children are returned in
            reverse document order.
        :returns: An iterator over the children.
        '''
        return self._children_rec(reverse)

    def descendants(self, reverse=False, depth_first=True, max_depth=None):
        '''\
        Returns an iterator over all descendants.

        :param reverse: If this is :const:`True` the descendants are returned
            in reverse document order.
        :type max_depth: :func:`bool`
        :param depth_first: If this is :const:`True` the descendants are
            returned depth-first, if it is :const:`False` breadth-first
            traversal is used.
        :type max_depth: :func:`bool`
        :param max_depth: The maximum depth, if this is :const:`None` all
            descendants will be returned.
        :type max_depth: :func:`int`
        :returns: An iterator over the descendants.
        '''
        reverse = bool(reverse)
        depth_first = bool(depth_first)
        if depth_first:
            child_reverse = not reverse
            pop_position = -1
        else:
            child_reverse = reverse
            pop_position = 0
        if max_depth is None:
            below_max_depth = lambda depth: True
            add_children = lambda current, depth: ((child, None)
                for child in current._children_rec(child_reverse))
        else:
            max_depth = int(max_depth)
            if max_depth < 1:
                raise ValueError(
                    'The argument "max_depth" must be greater than zero.')
            below_max_depth = lambda depth: depth < max_depth
            add_children = lambda current, depth: ((child, depth+1)
                for child in current._children_rec(child_reverse))
        nodes = list(add_children(self, 0))
        def iterator():
            while nodes:
                current, depth = nodes.pop(pop_position)
                yield current
                if (isinstance(current, ContainerNode)
                        and below_max_depth(depth)):
                    nodes.extend(add_children(current, depth))
        return iterator()

    def _children_rec(self, reverse):
        def iterator():
            for child in (reversed(self) if reverse else self):
                yield child
        return iterator()

    def _unwire_child(self, child):
        try:
            child._clear_namespace_uri()
        except AttributeError:
            pass
        try:
            del child._parent
        except AttributeError:
            pass
        self._wire_neighbors(child.previous, child.next)
        try:
            del child._next
        except AttributeError:
            pass
        try:
            del child._previous
        except AttributeError:
            pass

    def _wire_neighbors(self, left, right):
        if left is not None:
            left._next = right
        if right is not None:
            right._previous = left

    def _remove_from_parent(self, child):
        old_parent = child.parent
        if old_parent is not None:
            old_parent.remove(child)

    def _wire_child(self, index, child):
        child._parent = self
        if len(self) > 1:
            if index > 0:
                self._wire_neighbors(self[index-1], child)
            if index < len(self) - 1:
                self._wire_neighbors(child, self[index+1])
        try:
            child._clear_namespace_uri()
        except AttributeError:
            pass

    def __getitem__(self, index):
        return self._children[index]

    def __len__(self):
        return len(self._children)

    def __iter__(self):
        return self._children.__iter__()

    def __contains__(self, child):
        for current_child in self._children:
            if child is current_child:
                return True
        return False

    def __reversed__(self):
        return self._children.__reversed__()

    def __setitem__(self, index, child):
        self._remove_from_parent(child)
        try:
            old_child = self._children[index]
        except IndexError:
            old_child = None
        self._children[index] = child
        if old_child is not None:
            self._unwire_child(old_child)
        self._wire_child(index, child)

    def insert(self, index, child):
        '''\
        Insert ``child`` before ``index``.
        '''
        self._remove_from_parent(child)
        self._children.insert(index, child)
        self._wire_child(index, child)

    def __delitem__(self, index):
        child = self._children[index]
        del self._children[index]
        self._unwire_child(child)

    def remove(self, child):
        '''\
        Remove ``child``.
        '''
        for index, current_child in enumerate(self._children):
            if child is current_child:
                del self[index]
                return
        raise ValueError(child)


del abc, collections
