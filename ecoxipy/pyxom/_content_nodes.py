# -*- coding: utf-8 -*-

import abc
from xml.sax.xmlreader import AttributesImpl
from xml.sax.saxutils import XMLGenerator

from ecoxipy import _unicode
from ecoxipy import _helpers

from ._common import XMLNode, _string_repr


class ContentNode(XMLNode):
    '''\
    A :class:`XMLNode` with content.

    :param content: Becomes the :attr:`content` attribute.
    :type content: Unicode string
    '''
    __metaclass__ = abc.ABCMeta
    __slots__ = ('_content')

    def __init__(self, content):
        self._content = content

    @classmethod
    def create(cls, content):
        '''\
        Creates an instance of the :class:`ContentNode` implementation and
        converts ``content`` to an Unicode string.

        :param content: The content of the node. This will be converted to an
            Unicode string.
        :returns: The created :class:`ContentNode` implementation instance.
        '''
        return cls(_unicode(content))

    @property
    def content(self):
        '''\
        The node content. On setting the value is converted to an Unicode
        string.
        '''
        return self._content

    @content.setter
    def content(self, value):
        self._content = _unicode(value)

    def __eq__(self, other):
        return (isinstance(other, self.__class__)
            and self._content == other._content)

    def __ne__(self, other):
        return (not(isinstance(other, self.__class__))
            or self._content != other._content)


class Text(ContentNode):
    '''\
    A :class:`ContentNode` representing a node of text.
    '''
    def __repr__(self):
        return 'ecoxipy.pyxom.Text({})'.format(_string_repr(self.content))

    def _create_sax_events(self, content_handler, indent):
        content_handler.characters(self.content)

    def _create_str(self, out):
        return out.text(self.content)

    @_helpers.inherit_docstring(ContentNode)
    def duplicate(self):
        return Text(self.content)

    def __hash__(self):
        return object.__hash__(self)


class Comment(ContentNode):
    '''\
    A :class:`ContentNode` representing a comment node.

    :raises ecoxipy.XMLWellFormednessException: If ``check_well_formedness``
        is :const:`True` and ``content`` is not valid.
    '''
    __slots__ = ('_check_well_formedness')

    def __init__(self, content, check_well_formedness=False):
        if check_well_formedness:
            _helpers.enforce_valid_comment(content)
        ContentNode.__init__(self, content)
        self._check_well_formedness = check_well_formedness

    @staticmethod
    def create(content):
        '''\
        Creates a comment node.

        :param content: The content of the comment. This will be converted to an
            Unicode string.
        :returns: The created commment node.
        :rtype: :class:`Comment`
        :raises ecoxipy.XMLWellFormednessException: If ``content`` is not
            valid.
        '''
        content = _unicode(content)
        return Comment(content, True)

    def _create_str(self, out):
        return out.comment(self.content)

    def _create_sax_events(self, content_handler, indent):
        try:
            comment = content_handler.comment
        except AttributeError:
            return
        else:
            if indent:
                indent_incr, indent_count = indent
                content_handler.characters(u'\n')
                for i in range(indent_count):
                        content_handler.characters(indent_incr)
            comment(encode(self.content))

    def __repr__(self):
        return 'ecoxipy.pyxom.Comment({})'.format(_string_repr(self.content))

    @_helpers.inherit_docstring(ContentNode)
    def duplicate(self):
        return Comment(self.content)

    @ContentNode.content.setter
    def content(self, content):
        content = _unicode(content)
        if self._check_well_formedness:
            _helpers.enforce_valid_comment(content)
        self._content = content

    def __hash__(self):
        return object.__hash__(self)


class ProcessingInstruction(ContentNode):
    '''\
    A :class:`ContentNode` representing a processing instruction.

    :param target: The :attr:`target`.
    :param content: The :attr:`content` or :const:`None`.
    :param check_well_formedness: If :const:`True` the target will be checked
        to be a valid XML name.
    :type check_well_formedness: :func:`bool`
    :raises ecoxipy.XMLWellFormednessException: If ``check_well_formedness``
        is :const:`True` and either the ``target`` or the ``content`` are not
        valid.
    '''
    __slots__ = ('_target', '_check_well_formedness')

    def __init__(self, target, content, check_well_formedness=False):
        if check_well_formedness:
            _helpers.enforce_valid_pi_target(target)
            if content is not None:
                _helpers.enforce_valid_pi_content(content)
        ContentNode.__init__(self, content)
        self._target = target
        self._check_well_formedness = check_well_formedness

    @staticmethod
    def create(target, content=None):
        '''\
        Creates a processing instruction node and converts the parameters to
        appropriate types.

        :param target: The :attr:`target`, will be converted to an Unicode
            string.
        :param content: The :attr:`content`, if it is not :const:`None` it
            will be converted to an Unicode string.
        :returns: The created processing instruction.
        :rtype: :class:`ProcessingInstruction`
        :raises ecoxipy.XMLWellFormednessException: If either the ``target``
            or the ``content`` are not valid.
        '''
        target = _unicode(target)
        if content is not None:
            content = _unicode(content)
        return ProcessingInstruction(target, content, True)

    @property
    def target(self):
        '''\
        The processing instruction target.
        '''
        return self._target

    @target.setter
    def target(self, target):
        target = _unicode(target)
        if self._check_well_formedness:
            _helpers.enforce_valid_pi_target(target)
        self._target = _unicode(target)

    @ContentNode.content.setter
    def content(self, content):
        if content is not None:
            content = _unicode(content)
            if self._check_well_formedness:
                _helpers.enforce_valid_pi_content(content)
        self._content = content

    def _create_str(self, out):
        return out.processing_instruction(self._target, self.content)

    def _create_sax_events(self, content_handler, indent):
        if indent:
            indent_incr, indent_count = indent
            content_handler.characters(u'\n')
            for i in range(indent_count):
                    content_handler.characters(indent_incr)
        content_handler.processingInstruction(self.target,
            u'' if self.content is None else self.content)

    def __repr__(self):
        return 'ecoxipy.pyxom.ProcessingInstruction({}, {})'.format(
            _string_repr(self._target), _string_repr(self.content))

    def __eq__(self, other):
        return (isinstance(other, ProcessingInstruction)
            and self._target == other._target
            and self._content == other._content)

    def __ne__(self, other):
        return (not(isinstance(other, ProcessingInstruction))
            or self._target != other._target
            or self._content != other._content)

    @_helpers.inherit_docstring(ContentNode)
    def duplicate(self):
        return ProcessingInstruction(self._target, self.content)

    def __hash__(self):
        return object.__hash__(self)

del abc
