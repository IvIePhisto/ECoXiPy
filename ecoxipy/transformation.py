# -*- coding: utf-8 -*-
'''\

:mod:`ecoxipy.transformation` - Transforming XML
================================================

This module provides an XML transformation API. It containes the abstract
:class:`ecoxipy.Output` implementation :class:`MarkupTransformer`, which does
on-the-fly transformations while creating XML with the wrapped output
instance. Implementations of this class are used as output of
:class:`ecoxipy.MarkupBuilder` instances. Instances of
:class:`PyXOMTransformer` transform :mod:`ecoxipy.pyxom` data structures
in-place. The methods of implementations of these classes can be annotated
with the decorators in :attr:`MATCH` to serve as transformation callables --
if a transformation is the first who's test matches, it is applied and
transformation is finished. If no transformation callable matches, the node
is not transformed.


Examples
--------

We define a transformer which does:

*   Elements with an attribute ``href`` are converted to ``a`` links. If the
    element is a ``span``, it is directly converted to an ``a``, otherwise
    the original element is wrapped in an ``a``.

*   Processing instructions with target ``title`` are converted to an ``h1``
    element and set the instance variable ``_title``.

*   Text nodes with content ``foo bar`` are converted to upper case and
    wrapped into a ``strong`` element.

*   All comments are removed.

*   Documents with document type ``template`` are converted to a HTML5
    document using the instance variable ``_title``.


>>> class MyTransformer(MarkupTransformer):
...     @MATCH.element.test(
...             lambda name, children, attributes: 'href' in attributes)
...     def link(self, name, children, attributes):
...         if name == 'span':
...             return self.B.a(children, attributes)
...         href = attributes.pop('href')
...         return self.B.a(
...             self.B[name](children, attributes), href=href)
...
...     @MATCH.pi.title
...     def foo(self, target, content):
...         self._title = content
...         return self.B.h1(content)
...
...     @MATCH.text('foo bar')
...     def foo_bar(self, content):
...         return self.B.strong(content.upper())
...
...     @MATCH.comment()
...     def comment(self, content):
...         pass
...
...     @MATCH.document.template
...     def doc(self, *args):
...         B = self.B
...         return B[:'html':True]('\\n',
...             B.html('\\n',
...                 B.head(B.title(self._title)), '\\n',
...                 B.body('\\n', args[3], '\\n'), '\\n',
...             )
...         )


We create an example document, using the transformer:

>>> from ecoxipy import MarkupBuilder
>>> B = MyTransformer.builder()
>>> print(B[:'template':True](
...     B['title':'Test'], '\\n',
...     B | 'This comment will be removed.',
...     B.p('\\n',
...         B.span('Example Site', href='http://example.com'), '\\n',
...         'foo bar', '\\n',
...         B.em('Example Site', href='http://example.com', lang='en'), '\\n'
...     )
... ))
<!DOCTYPE html>
<html>
<head><title>Test</title></head>
<body>
<h1>Test</h1>
<p>
<a href="http://example.com">Example Site</a>
<strong>FOO BAR</strong>
<a href="http://example.com"><em lang="en">Example Site</em></a>
</p>
</body>
</html>


API
---

.. autoclass:: MarkupTransformer
    :no-members:

.. attribute:: MATCH

    .. attribute:: .element

    .. attribute:: .text

    .. attribute:: .comment

    .. attribute:: .pi

    .. attribute:: .document

'''

import abc

from tinkerpy import metaclass

from ecoxipy import _unicode


NODE_TYPES = ('element', 'processing_instruction', 'text', 'comment',
            'document')


class MATCH(object):
    class _AddMatch(object):
        def __init__(self, node_type):
            self._attribute_name = '_MATCH_' + node_type

        def test(self, test):
            def decorator(func):
                import inspect
                stack = inspect.stack()
                frame = stack[1][0]
                caller_locals = frame.f_locals
                del stack, frame
                try:
                    match_list = caller_locals[self._attribute_name]
                except KeyError:
                    match_list = []
                    caller_locals[self._attribute_name] = match_list
                match_list.append((test, func.__name__))
                return func
            return decorator

        def __call__(self, *infos):
            if len(infos) == 0:
                test = lambda *args: True
            else:
                test = lambda *args: infos == args[:len(infos)]
            return self.test(test)

        __getattr__ = __call__

    element = _AddMatch('element')
    pi = _AddMatch('processing_instruction')
    text = _AddMatch('text')
    comment = _AddMatch('comment')
    document = _AddMatch('document')
    del _AddMatch

MATCH = MATCH()


class _Transformer(object):
    '''Internal base class for transformers.'''
    class MATCH_SPEC(object):
        def _init_cls(self, cls):
            match_infos = {node_type: [] for node_type in NODE_TYPES}
            for base_cls in cls.__mro__:
                for node_type in NODE_TYPES:
                    try:
                        node_type_infos = getattr(base_cls,
                            '_MATCH_' + node_type)
                    except AttributeError:
                        pass
                    else:
                        match_infos[node_type].extend(node_type_infos)
            cls._MATCH_SPEC = match_infos

        def _init_obj(self, obj, cls):
            cls_match_infos = cls._MATCH_SPEC
            obj_match_infos = {}
            for node_type in cls_match_infos:
                node_type_infos = []
                obj_match_infos[node_type] = node_type_infos
                for test, meth_name in cls_match_infos[node_type]:
                    meth = getattr(obj, meth_name)
                    node_type_infos.append((test, meth))
            obj._MATCH_SPEC = obj_match_infos

        def __get__(self, obj, cls):
            if '_MATCH_SPEC' not in cls.__dict__:
                self._init_cls(cls)
            if obj is None:
                return cls._MATCH_SPEC
            if '_MATCH_SPEC' not in obj.__dict__:
                self._init_obj(obj, cls)
            return obj._MATCH_SPEC

        def __set__(self, obj, value):
            raise AttributeError()

    MATCH_SPEC = MATCH_SPEC()

    def __init__(self, output=None, input_encoding='UTF-8', parser=None):
        self._output = output
        self._input_encoding = input_encoding
        self._parser = parser
        if output is None:
            self.B
            self._output = self.B._output

    @property
    def output(self):
        return self._output

    @property
    def B(self):
        try:
            return self._builder
        except AttributeError:
            from ecoxipy import MarkupBuilder
            builder = MarkupBuilder(self._output, self._input_encoding,
                self._parser)
            self._builder = builder
            return builder

    def default_transformer(self, node_type):
        return getattr(self.output, node_type)

    def transformer(self, node_type):
        match_spec = self.MATCH_SPEC[node_type]
        default_transformer = self.default_transformer(node_type)
        def transform(*args):
            for test, method in match_spec:
                if test(*args):
                    return method(*args)
            return default_transformer(*args)
        return transform

    @classmethod
    def builder(cls, *args, **kargs):
        from ecoxipy import MarkupBuilder
        transformer = cls(*args, **kargs)
        builder = MarkupBuilder(transformer, transformer._input_encoding,
            transformer._parser)
        return builder


@metaclass(abc.ABCMeta)
class MarkupTransformer(_Transformer):
    '''\
    Base transformer class that implements the :class:`ecoxipy.Output`
    interface.

    Extend it and annotate your methods with the decorators contained in
    :attr:`MATCH`. These methods must have a signature compatible with the
    appropriate methods of :class:`ecoxipy.Output`, i.e. a method annotated with
    `MATCH.element` must conform to :meth:`ecoxipy.Output.element`. Their return
    values replace the content otherwise created, if there were no
    transformation. The methods should use the builder contained in the
    attribute :attr:`B` to create XML structures, then they are independent of
    the :class:`ecoxipy.Output` implementation given on intitialization.

    Your class should not override the methods as defined by
    :class:`ecoxipy.Output` and the following attributes:

    *   ``B``
    *   ``builder``
    *   ``default_transformer``
    *   ``MATCH_SPEC``
    *   ``transformer``
    *   ``output``
    '''
    def __init__(self, output=None, input_encoding='UTF-8', parser=None):
        _Transformer.__init__(self, output, input_encoding, parser)
        for node_type in NODE_TYPES:
            setattr(self, node_type, self.transformer(node_type))

    def is_native_type(self, content):
        return self._output.is_native_type(content)

    def fragment(self, children):
        return self._output.fragment(children)


# TODO: add to documentation
# TODO: add tests
@metaclass(abc.ABCMeta)
class PyXOMTransformer(_Transformer):
    '''\
    Base transformer class that works on :mod:`ecoxipy.pyxom` nodes. Instances
    of this class are callable with an arbitrary number of PyXOM nodes as the
    arguments to be transformed. The result of such a call is a XML structure in
    the output representation configured by the intitialization argument
    ``output``.

    Extend it and annotate your methods with the decorators contained in
    :attr:`MATCH`. These methods must take an PyXOM node of the class
    appropriate for the match, i.e. methods match a document will receive
    :class:`ecoxipy.pyxom.Document` instances. They should return XML structures
    in the output representation using the builder contained in the
    attribute :attr:`B`. The transformation methods are called with the matching
    node instances and their return value is used in place of the XML structure
    otherwise created from the given node.

    Your class should not override the following attributes:

    *   ``__call__``
    *   ``_apply``
    *   ``_queue``
    *   ``B``
    *   ``builder``
    *   ``comment``
    *   ``default_transformer``
    *   ``document``
    *   ``element``
    *   ``fragment``
    *   ``MATCH_SPEC``
    *   ``output``
    *   ``processing_instruction``
    *   ``text``
    *   ``transformer``
    '''
    def __init__(self, output=None, input_encoding='UTF-8', parser=None):
        _Transformer.__init__(self, output, input_encoding, parser)
        from ecoxipy.pyxom import (Element, ProcessingInstruction, Text,
            Comment, Document)
        self._transforms = {
            Element: self.transformer('element'),
            ProcessingInstruction: self.transformer('processing_instruction'),
            Text: self.transformer('text'),
            Comment: self.transformer('comment'),
            Document: self.transformer('document')
        }

    from collections import deque as _queue

    def default_transformer(self, node_type):
        return getattr(self, node_type)

    def element(self, node):
        return self.output.element(node.name, self._apply(node),
            node.attributes.to_dict())

    def processing_instruction(self, node):
        return self.output.processing_instruction(node.target, node.content)

    def text(self, node):
        return self.output.text(node.content)

    def comment(self, node):
        return self.output.comment(node.content)

    def document(self, node):
        doctype = node.doctype
        return self.output.document(doctype.name, doctype.publicid,
            doctype.systemid, self._apply(node), node.omit_xml_declaration)

    def fragment(self, children):
        return self.output.fragment(children)

    def _apply(self, nodes):
        return self._queue(self._transforms[node.__class__](node)
            for node in nodes)

    def __call__(self, *nodes):
        results = self._apply(nodes)
        if len(results) == 1:
            return results.popleft()
        return results

del abc