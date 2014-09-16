# -*- coding: utf-8 -*-
'''\

:mod:`ecoxipy.validation` - Validating XML
==========================================

This module provides the :class:`ecoxipy.Output` implementation
:class:`ValidationOutputWrapper`, which validates the XML created using a
validator object. The class :class:`ListValidator` is a validator
implementation working based on black- or whitelists.

To use validation for markup builders, use instances of this class:

.. autoclass:: ValidationOutputWrapper
    :no-members:


Validators should throw the following exception:

.. autoclass:: ValidationError


A simple black- or whitelist validator:

.. autoclass:: ListValidator
    :no-members:


.. _ecoxipy.validation.examples:

Examples
--------

First we define a blacklist validator and use it to define a markup builder:

>>> blacklist = ListValidator(['script', 'style'], ['onclick', 'style'], ['xml-stylesheet'])

>>> from ecoxipy import MarkupBuilder
>>> from ecoxipy.string_output import StringOutput
>>> output = ValidationOutputWrapper(StringOutput(), blacklist)
>>> b = MarkupBuilder(output)

Here we create XML, invalid nodes are not created:

>>> print(b.p(
...     b['xml-stylesheet': 'href="BadStyling.css"'],
...     b['my-pi': 'info'],
...     b.script('InsecureCode();'),
...     'Hello ', b.em(
...         'World', {'class': 'important', 'onclick': 'MalicousThings();'}),
...     '!'
... ))
<p><?my-pi info?>Hello <em class="important">World</em>!</p>


And now we define a whitelist validator, which is not silent but raisese
exeptions on validation errors:

>>> whitelist = ListValidator(['p', 'em'], ['class'], ['my-pi'], False, False)

>>> output = ValidationOutputWrapper(StringOutput(), whitelist)
>>> b = MarkupBuilder(output)

First we create valid XML, then some invalid XML:

>>> print(b.p(
...     b['my-pi': 'info'],
...     'Hello ', b.em('World', {'class': 'important'}), '!'
... ))
<p><?my-pi info?>Hello <em class="important">World</em>!</p>

>>> try:
...     b['xml-stylesheet': 'href="BadStyling.css"']
... except ValidationError as e:
...     print(e)
The processing instruction target "xml-stylesheet" is not allowed.

>>> try:
...     b.script('InsecureCode();')
... except ValidationError as e:
...     print(e)
The element name "script" is not allowed.

>>> try:
...     b.em('World', {'class': 'important', 'onclick': 'MalicousThings();'})
... except ValidationError as e:
...     print(e)
The attribute name "onclick" is not allowed.


If one of the element, attribute or processing instruction validity lists of
:class:`ListValidator` is :const:`None`, it allows all nodes of that type:

>>> anything = ListValidator()
>>> output = ValidationOutputWrapper(StringOutput(), anything)
>>> b = MarkupBuilder(output)
>>> print(b.p(
...     b['my-pi': 'info'],
...     'Hello ', b.em('World', {'class': 'important'}), '!'
... ))
<p><?my-pi info?>Hello <em class="important">World</em>!</p>

>>> anything = ListValidator(blacklist=False)
>>> output = ValidationOutputWrapper(StringOutput(), anything)
>>> b = MarkupBuilder(output)
>>> print(b.p(
...     b['my-pi': 'info'],
...     'Hello ', b.em('World', {'class': 'important'}), '!'
... ))
<p><?my-pi info?>Hello <em class="important">World</em>!</p>

'''

from ecoxipy import _unicode


class ValidationOutputWrapper(object):
    '''\
    Instances of this class wrap an :class:`ecoxipy.Output` instance and a
    validator instance, the latter having a method like
    :class:`ecoxipy.Output` for each XML node type it wishes to validate (i.e.
    :meth:`element`, :meth:`text`, :meth:`comment`,
    :meth:`processing_instruction` and :meth:`document`).

    When a XML node is to be created using this class, first the appropriate
    validator method is called. This might raise an exception to stop building
    completely. If this returns :const:`None` or :const:`True`, the result of
    calling the same method on the output instance is returned. Otherwise
    the creation call returns :const:`None` to create nothing.

    Note that a validator's :meth:`element` method receives the attributes
    dictionary which is given to the output, thus changes made by a validator
    are reflected in the created XML representation.
    '''
    def __init__(self, output, validator):
        self._output = output
        self._validator = validator
        self._ValidationMethod(self, 'element')
        self._ValidationMethod(self, 'text')
        self._ValidationMethod(self, 'comment')
        self._ValidationMethod(self, 'processing_instruction')
        self._ValidationMethod(self, 'document')
        try:
            self.preprocess = output.preprocess
        except AttributeError:
            pass

    class _ValidationMethod(object):
        def __init__(self, wrapper, name):
            try:
                self._validation_method = getattr(wrapper._validator, name)
            except AttributeError:
                self._validation_method = None
            self._creation_method = getattr(wrapper._output, name)
            setattr(wrapper, name, self)

        def __call__(self, *args):
            if self._validation_method is None:
                validation_result = None
            else:
                validation_result = self._validation_method(*args)
            if validation_result is None or validation_result is True:
                return self._creation_method(*args)

    def is_native_type(self, content):
        return self._output.is_native_type(content)


class ValidationError(Exception):
    '''\
    Should be raised by validators to indicate a error while validating, the
    message should describe the problem.
    '''


class ListValidator(object):
    '''\
    A simple black- or whitelist-based validator class (see
    :class:`ValidationOutputWrapper`). It takes lists of element as well as
    attribute names and processing instruction targets, all given names and
    targets are converted to Unicode. If the ``blacklist`` argument is
    :const:`True` the lists define which elements, attributes and processing
    instructions are invalid. If ``blacklist`` is :const:`False` the instance
    works as a whitelist, thus the lists define the valid elements, attributes
    and processing instructions. If the argument ``silent`` is :const:`True`,
    the validating methods return :const:`False` on validation errors,
    otherwise they raise a :class:`ValidationError`.

    :param element_names: An iterable of element names or :const:`None` to
        accept all elements.
    :param attribute_names: An iterable of attribute names or :const:`None` to
        accept all attributes.
    :param pi_targets: An iterable of processing instruction targets or
        :const:`None` to accept all processing instructions.
    :param blacklist: If this is :const:`True`, the instance works as a
        blacklist, otherwise as a whitelist.
    :type blacklist: :class:`bool`
    :param silent: If this is :const:`True`, failed validations return
        :const:`False` for invalid element names or processing instruction
        targets and invalid attributes are deleted. Otherwise they raise a
        :class:`ValidationError`.
    :type silent: :class:`bool`
    '''
    def __init__(self, element_names=None, attribute_names=None,
            pi_targets=None, blacklist=True, silent=True):
        if bool(blacklist):
            self._invalid = self._blacklist_invalid
            none_container = self._NothingContainer
        else:
            self._invalid = self._whitelist_invalid
            none_container = self._EverythingContainer
        create_set = lambda items: (none_container if items is None
            else {_unicode(item) for item in items})
        self._element_names = create_set(element_names)
        self._attribute_names = create_set(attribute_names)
        self._pi_targets = create_set(pi_targets)
        self._silent = bool(silent)

    @staticmethod
    def _whitelist_invalid(item, allowed):
        return item not in allowed

    @staticmethod
    def _blacklist_invalid(item, forbidden):
        return item in forbidden

    class _EverythingContainer(object):
        def __contains__(self, item):
            return True

    _EverythingContainer = _EverythingContainer()

    class _NothingContainer(object):
        def __contains__(self, item):
            return False

    _NothingContainer = _NothingContainer()

    def element(self, name, children, attributes):
        if self._invalid(name, self._element_names):
            if self._silent:
                return False
            raise ValidationError(
                'The element name "{}" is not allowed.'.format(name))
        for attr_name in list(attributes.keys()):
            if self._invalid(attr_name, self._attribute_names):
                if self._silent:
                    del attributes[attr_name]
                else:
                    raise ValidationError(
                        'The attribute name "{}" is not allowed.'.format(
                            attr_name))

    def processing_instruction(self, target, content):
        if self._invalid(target, self._pi_targets):
            if self._silent:
                return False
            raise ValidationError(
                'The processing instruction target "{}" is not allowed.'.format(
                    target))

