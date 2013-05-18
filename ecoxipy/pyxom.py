# -*- coding: utf-8 -*-
'''\
PyXOM - Pythonic XML Object Model
=================================

This module implements a pythonic object model for the representation of XML
structures. To create PyXOM data conveniently use :mod:`ecoxipy.pyxom_output`.

Examples
--------
>>> document = Document(u'html', None, None, [
...     Element(u'html', [
...         Element(u'head', [
...             Element(u'title', [Text(u'The Title')], {}),
...         ], {}),
...         Element(u'body', [Text(u'Hello World!')], {}),
...         ProcessingInstruction(u'target', u'content'),
...         Comment(u'Comment Content'),
...     ], {u'xmlns': u'http://www.w3.org/1999/xhtml/'})
... ], True, None)
>>> print(str(document))
<!DOCTYPE html><html xmlns="http://www.w3.org/1999/xhtml/"><head><title>The Title</title></head><body>Hello World!</body><?target content?><!--Comment Content--></html>
>>> for node in document[0][1:]:
...     print(str(node))
<body>Hello World!</body>
<?target content?>
<!--Comment Content-->
'''
# TODO finish doctests, especially of paths

bla = '''
Getting the :func:`bytes` value of an document yields an encoded byte string:

>>> document_string = u"""<!DOCTYPE section><article lang="en"><h1 data="to quote: &lt;&amp;&gt;&quot;'">&lt;Example&gt;</h1><p umlaut-attribute="äöüß">Hello<em count="1"> World</em>!</p><div><data-element>äöüß &lt;&amp;&gt;</data-element><p attr="value">raw content</p>Some Text<br/>012345</div><!--<This is a comment!>--><?pi-target <PI content>?><?pi-without-content?></article>"""
>>> import sys
>>> (unicode(doc) if sys.version_info[0] < 3 else str(doc)) == document_string
True


Getting the :func:`bytes` value of an :class:`Document` creates a byte string
with the encoding specified on creation of the instance, it defaults
to "UTF-8":

>>> bytes(doc) == document_string.encode('UTF-8')
True


:class:`XMLNode` instances can also generate SAX events, see
:meth:`XMLNode.create_sax_events` (note that the default
:class:`xml.sax.ContentHandler` is :class:`xml.sax.saxutils.ContentHandler`,
which does not support comments):

>>> document_string = u"""<?xml version="1.0" encoding="UTF-8"?>\\n<article lang="en"><h1 data="to quote: &lt;&amp;&gt;&quot;'">&lt;Example&gt;</h1><p umlaut-attribute="äöüß">Hello<em count="1"> World</em>!</p><div><data-element>äöüß &lt;&amp;&gt;</data-element><p attr="value">raw content</p>Some Text<br></br>012345</div><?pi-target <PI content>?><?pi-without-content ?></article>"""
>>> if sys.version_info[0] > 2:
...     from io import StringIO
...     string_io = StringIO
... else:
...     from io import BytesIO
...     string_io = BytesIO
...     document_string = document_string.encode('UTF-8')
>>> string_out = string_io()
>>> content_handler = doc.create_sax_events(out=string_out)
>>> string_out.getvalue() == document_string
True
>>> string_out.close()


You can also create indented XML when calling the
:meth:`XMLNode.create_sax_events` by supplying the ``indent_incr`` argument:

>>> indented_document_string = u"""\\
... <?xml version="1.0" encoding="UTF-8"?>
... <article lang="en">
...     <h1 data="to quote: &lt;&amp;&gt;&quot;'">
...         &lt;Example&gt;
...     </h1>
...     <p umlaut-attribute="äöüß">
...         Hello
...         <em count="1">
...              World
...         </em>
...         !
...     </p>
...     <div>
...         <data-element>
...             äöüß &lt;&amp;&gt;
...         </data-element>
...         <p attr="value">
...             raw content
...         </p>
...         Some Text
...         <br></br>
...         012345
...     </div>
...     <?pi-target <PI content>?>
...     <?pi-without-content ?>
... </article>
... """
>>> if sys.version_info[0] <= 2:
...     indented_document_string = indented_document_string.encode('UTF-8')
>>> string_out = string_io()
>>> content_handler = doc.create_sax_events(indent_incr='    ', out=string_out)
>>> string_out.getvalue() == indented_document_string
True
>>> string_out.close()


Classes
-------
'''

import abc
import ast
import collections
import xml.sax
import xml.sax.xmlreader
import xml.sax.saxutils

from ecoxipy import _python3, _unicode
import ecoxipy.string_output


class XMLNode(object):
    '''\
    Base class for XML node objects.

    Retrieving the byte string from an instance yields a byte string encoded
    as `UTF-8`.
    '''
    __metaclass__ = abc.ABCMeta
    __slots__ = ('_parent')

    @property
    def parent(self):
        '''\
        The parent :class:`ContainerNode` or :const:`None` if the node has no
        parent.
        '''
        try:
            return self._parent
        except AttributeError:
            return None

    def ancestors(self, test=None):
        '''\
        Returns iterator over all ancestors.
        '''
        if test is None:
            test = lambda context: True
        current = self
        def iterator():
            current = current.parent
            while True:
                if current is None:
                    break
                elif test(current):
                    yield current
        return iterator()

    def __str__(self):
        '''\
        Creates a Unicode string containing the XML representation of
        the node.
        '''
        return self.create_str()

    def __bytes__(self):
        '''\
        Creates a byte string containing the XML representation of the
        node.
        '''
        return self.create_str(encoding='UTF-8')

    if not _python3:
        __unicode__ = __str__
        __str__ = __bytes__
        del __bytes__


    def create_str(self, out=None, encoding=None):
        '''\
        Creates a string containing the XML representation of the node.

        :param out: A :class:`ecoxipy.string_output.StringOutput` instance or
            :const:`None`. If it is the latter, a new
            :class:`ecoxipy.string_output.StringOutput` instance is created.
        :param encoding: The output encoding or :const:`None` for Unicode
            output. Is only taken into account if ``out`` is :const:`None`.
        '''
        if out is None:
            out = ecoxipy.string_output.StringOutput()
        output_string = self._create_str(out)
        if encoding is not None and not isinstance(output_string, bytes):
            output_string = output_string.encode(encoding)
        return output_string

    @abc.abstractmethod
    def _create_str(self, out):
        '''\
        Creates a string containing the XML representation of the node.

        :param out: A :class:`ecoxipy.string_output.StringOutput` instance.
        '''
        pass

    def create_sax_events(self, content_handler=None, out=None,
            out_encoding='UTF-8', indent_incr=None):
        '''\
        Creates SAX events.

        :param content_handler: If this is :const:`None` a
            ``xml.sax.saxutils.XMLGenerator`` is created and used as the
            content handler. If in this case ``out`` is not :const:`None`,
            it is used for output.
        :type content_handler: :class:`xml.sax.ContentHandler`
        :param out: The output to write to if no ``content_handler`` is given.
            It should have a ``write`` method like files.
        :param out_encoding: The output encoding if no ``content_handler``
            is given and ``out`` is not :const:`None`.
        :param indent_incr: If this is not :const:`None` this activates
            pretty printing. In this case it should be a string and it is used
            for indenting.
        :type indent_incr: :func:`str`
        :returns: The content handler used.
        '''
        if content_handler is None:
            content_handler = xml.sax.saxutils.XMLGenerator(out, out_encoding)
        if indent_incr is None:
            indent = False
        else:
            indent_incr = _unicode(indent_incr)
            indent = (indent_incr, 0)
        self._create_sax_events(content_handler, indent)
        return content_handler

    @abc.abstractmethod
    def _create_sax_events(self, content_handler, indent):
        pass

    @abc.abstractmethod
    def __repr__(self):
        pass


class Text(XMLNode):
    __slots__ = ('_value', '_parent')

    def __init__(self, value):
        self._value = value

    @property
    def value(self):
        return self._value

    def __repr__(self):
        return 'ecoxipy.pyxom.Text({})'.format(repr(self._value))

    def _create_sax_events(self, content_handler, indent):
        content_handler.characters(self.value)

    def _create_str(self, out):
        return out.text(self._value)


class ContainerNode(XMLNode, collections.MutableSequence):
    __slots__ = ('_children')

    def __init__(self, children):
        self._children = children
        for child in children:
            child._parent = self

    def __getitem__(self, index):
        return self._children[index]

    def __setitem__(self, index, child):
        child._parent = self
        self._children[index] = child

    def insert(self, index, child):
        child._parent = self
        self._children.insert(index, child)

    def __delitem__(self, index):
        child = self._children[index]
        del child._parent
        del self._children[index]

    def __len__(self):
        return len(self._children)

    def __iter__(self):
        return self._children.__iter__()

    def __contains__(self, item):
        return item in self._children

    def __call__(self, *path):
        return Finder.find(self, path)

    def descendants(self, test=None, document_order=True):
        '''\
        Returns iterator over all descendants.
        '''
        if document_order:
            children = self
        else:
            children = reversed(self)
        if test is None:
            test = lambda context: True
        def iterator():
            for child in children:
                try:
                    for descendant in child.descendants(document_order):
                        if test(descendant):
                            yield descendant
                except AttributeError:
                    if test(child):
                        yield child
        return iterator()


class PyXOMPL(object):
    doctest='''\

    >>> p('html/body/ancestor>div/attributes>"data-foo"/bar/parent>True/parent>True/p')
    >>> p('html/body//(div and where(attributes>"data-foo"/bar))/p')
    >>> p('html/body//(div and {"data-foo":bar})/p')

    >>> p('html/body/ancestor>(div or True/attributes>"data-foo"/bar/parent>True/parent>True)/p')
    >>> p('html/body//(div or where(attributes>"data-foo"/bar))/p')
    >>> p('html/body//(div or {"data-foo":bar})/p')

    >>> p(\'''html/body//pi()/`re.findall(r' href=".+?"', _)`/parent>True''\')
    >>> p(\'''html/body//pi(True, `re.findall(r' href=".+?"', _)`)\')
    >>> p(\'''html/body//(pi() and where(`re.findall(r' href=".+?"', _)`))''\')

    >>> p(\'''html/body//comment()/`_.startswith('TODO')`/parent>True''\')
    >>> p(\'''html/body//comment(`_.startswith('TODO')`)''\')
    >>> p(\'''html/body//comment() and where(`_.startswith('TODO')`)''\')

    `text` := identifier | stringliteral

    `boolean_expression` := `test` (``and`` | ``or`` ) `test` | ``not`` `test`

    `python_expression` := ``\``` expression ``\```

    `test` := `text` | `boolean_expression` | `python_expression`

    `element_test` := `test` | ``element(`` `test` ``)``

    `text_test` := ``text(`` [`test`] ``)``

    `comment_test` := ``comment(`` [`test`] ``)``

    `pi_test` := ``pi(`` [`test` [``,`` `test`]] ``)``

    `document_test` := ``document(`` `test` [``,`` `test` [``,`` `test`]] ``)``

    `attrs_test` := ``{`` ([`test` ``:`` `test` [``,`` `test` ``:`` `test`] ] | (`test` [``,`` `test`]*)+) ``}``

    `node_test` := `element_test` | `text_test` | `pi_test` | `comment_test` | `document_test`

    `forward_axis` := `self` | `child` | `descendant` | `attribute` | `following` | `following-sibling`

    `reverse_axis` := `parent` | `ancestor` | `preceding` | `preceding-sibling`

    `step` := [`axis` ``>``] `node_test` [``[`` index | slice ``]``]

    `path` := `step` (``/`` `step`)*

    '''
    class _NodeVisitor(ast.NodeTransformer):
        def generic_visit(self, node):
            return ast.NodeTransformer.generic_visit(self, node)

    def __init__(self, path):
        self._steps = self._compile(path)

    @classmethod
    def _compile(self, path):
        path_ast = compile(path, '<ecoxipy.pyxom.PyXOMPL: {}>'.format(path),
            'eval',ast.PyCF_ONLY_AST)
        print(ast.dump(path_ast, False))
        visitor = self._NodeVisitor()
        visitor.visit(path_ast)
        print('---TRANSFORMED:---')
        print(ast.dump(path_ast, False))


class NodeFinder(object):
    @staticmethod
    def _test_node(name):
        if name == '*':
            return lambda context: isinstance(context, Element)
        if name == '$':
            return lambda context: isinstance(context, Text)
        if name.startwith('!'):
            if len(name) == 1:
                return lambda context: isinstance(context, Comment)
            name = name[1:]
            return lambda context: (isinstance(context, Comment)
                and context.content == name)
        if name.startwith('?'):
            if len(name) == 1:
                return lambda context: isinstance(context,
                    ProcessingInstruction)
            name = name[1:]
            try:
                target, content = name.split(' ')
            except ValueError:
                return lambda context: isinstance(context,
                    ProcessingInstruction) and context.target == name
            return lambda context: (
                isinstance(context, ProcessingInstruction)
                and context.target == name and context.content == content
            )
        return lambda context: (isinstance(context, Element)
            and context.name == name)

    @staticmethod
    def _test_attributes(attributes):
        def _test(context):
            try:
                _attributes = context.attributes
            except AttributeError:
                return False
            for attr_name, attr_value in attributes.items():
                if attr_name in _attributes:
                    if attr_value is not None:
                        if attr_value != _attributes[attr_name]:
                            return False
                else:
                    return False
            return True
        return _test

    @classmethod
    def _test_or(cls, sequence):
        tests = [cls.create_test(item) for item in sequence]
        def _test(context):
            for test in tests:
                if test(context):
                    return True
            return False
        return _test

    @classmethod
    def create_test(cls, spec):
        if isinstance(spec, collections.Sequence):
            return cls._test_or(spec)
        elif isinstance(spec, collections.Mapping):
            return cls._test_attributes(spec)
        elif isinstance(spec, collections.Callable):
            return spec
        if not isinstance(spec, _unicode):
            spec = _unicode(spec)
        return cls._test_node(_unicode(spec))

    @classmethod
    def find(self, context, path):
        if len(path) == 0:
            return context
        for step in path:
            if step is None:
                context = list(context)
            elif isinstance(step, int):
                context = context[step]
            else:
                context = filter(self.create_test(step), context)
        return context


class Document(ContainerNode):
    '''\
    Represents a XML document.

    :param doctype_name: The document type root element name or :const:`None`
        if the document should not have document type declaration.
    :param doctype_publicid: The public ID of the document type declaration.
    :param doctype_publicid: The system ID of the document type declaration.
    :param children: The document root nodes.
    :param encoding: The encoding of the document. If it is :const:`None`
        `UTF-8` is used.
    :param omit_xml_declaration: If :const:`True` the XML declaration is
        omitted.
    '''
    __slots__ = ('_doctype', '_omit_xml_declaration')

    DocumentType = collections.namedtuple('DocumentType',
        'name publicid systemid')
    '''\
    Represents a document type declaration.

    :param name: The document element name.
    :param publicid: The document type public ID.
    :param systemid: The document type system ID.
    '''

    def __init__(self, doctype_name, doctype_publicid, doctype_systemid,
            children, omit_xml_declaration, encoding):
        ContainerNode.__init__(self, children)
        if doctype_name is None:
            self._doctype = None
        else:
            doctype_name = doctype_name
            self._doctype = self.DocumentType(doctype_name, doctype_publicid,
                doctype_systemid)
        self._omit_xml_declaration = omit_xml_declaration
        if encoding is None:
            encoding = 'UTF-8'
        self._encoding = encoding

    @property
    def doctype(self):
        '''\
        The :class:`Doctype` instance of the document or :const:`None`.
        '''
        return self._doctype

    @property
    def omit_xml_declaration(self):
        '''\
        If :const:`True` the XML declaration is omitted.
        '''
        return self._omit_xml_declaration

    @property
    def encoding(self):
        '''\
        The encoding of the document.
        '''
        return self._doctype

    def __bytes__(self):
        '''\
        Creates a byte string containing the XML representation of the
        node with the encoding :meth:`encoding`.
        '''
        return self.create_str(encoding=self._encoding)

    if not _python3:
        __str__ = __bytes__
        del __bytes__

    def create_sax_events(self, content_handler=None, out=None,
            out_encoding='UTF-8', indent_incr=None):
        '''\
        Creates SAX events.

        :param content_handler: If this is :const:`None` a
            ``xml.sax.saxutils.XMLGenerator`` is created and used as the
            content handler. If in this case ``out`` is not :const:`None`,
            it is used for output.
        :type content_handler: :class:`xml.sax.ContentHandler`
        :param out: The output to write to if no ``content_handler`` is given.
            It should have a ``write`` method like files.
        :param out_encoding: This is not taken into account, instead
            :meth:`encoding` is used  if no ``content_handler``
            is given and ``out`` is not :const:`None`.
        :param indent_incr: If this is not :const:`None` this activates
            pretty printing. In this case it should be a string and it is used
            for indenting.
        :type indent_incr: :func:`str`
        :returns: The content handler used.
        '''
        return XMLNode.create_sax_events(self, content_handler, out,
            self._encoding, indent_incr)

    def _create_str(self, out):
        return out.document(self._doctype.name, self._doctype.publicid,
            self._doctype.systemid, [
                child._create_str(out) for child in self
            ], self._omit_xml_declaration, self._encoding)

    def _create_sax_events(self, content_handler, indent):
        content_handler.startDocument()
        try:
            notationDecl = content_handler.notationDecl
        except AttributeError:
            pass
        else:
            notationDecl(self._doctype.name, self._doctype.publicid,
                self._doctype.systemid)
        for child in self:
            child._create_sax_events(content_handler, indent)
        content_handler.endDocument()

    def __repr__(self):
        return 'ecoxipy.pyxom.Document(*{}, [...], {}, {})'.format(
            repr(self._doctype), self._omit_xml_declaration, self._encoding
        )


class Element(ContainerNode):
    '''\
    Represents a XML element.

    :param name: The name of the element to create.
    :param children: The children of the element.
    :type children: iterable of items
    :param attributes: The attributes of the element.
    :type attributes: subscriptable iterable over keys
    '''

    __slots__ = ('_name', '_attributes')

    def __init__(self, name, children, attributes):
        ContainerNode.__init__(self, children)
        self._name = name
        self._attributes = attributes

    @property
    def name(self):
        '''The name of the element.'''
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def attributes(self):
        '''\
        An :func:`dict` containing the element's attributes. The key
        represents an attribute's name, the value is the attribute's value.
        '''
        return self._attributes

    def _create_str(self, out):
        return out.element(self.name, [
                child._create_str(out) for child in self
            ], self.attributes)

    def _create_sax_events(self, content_handler, indent):
        if indent:
            indent_incr, indent_count = indent
            child_indent = (indent_incr, indent_count + 1)
        else:
            child_indent = indent
        def do_indent(at_start=False):
            if indent:
                if indent_count > 0 or not at_start:
                    content_handler.characters('\n')
                for i in range(indent_count):
                    content_handler.characters(indent_incr)
        do_indent(True)
        attributes = xml.sax.xmlreader.AttributesImpl(self.attributes)
        content_handler.startElement(self.name, attributes)
        last_event_characters = False
        for child in self:
            if isinstance(child, XMLNode):
                child._create_sax_events(
                    content_handler, child_indent)
                last_event_characters = False
            else:
                if indent and not last_event_characters:
                    do_indent()
                    content_handler.characters(indent_incr)
                content_handler.characters(child)
                last_event_characters = True
        if len(self) > 0:
            do_indent()
        content_handler.endElement(self.name)
        if indent and indent_count == 0:
            content_handler.characters('\n')

    def __repr__(self):
        return 'ecoxipy.pyxom.Element({}, [...], {})'.format(
            repr(self._name), repr(self._attributes)
        )


class Comment(XMLNode):
    '''\
    Represent a comment.

    :param content: The comment content.
    '''
    __slots__ = ('_content')

    def __init__(self, content):
        self._content = content

    @property
    def content(self):
        return self._content

    def _create_str(self, out):
        return out.comment(self._content)

    def _create_sax_events(self, content_handler, indent):
        try:
            comment = content_handler.comment
        except AttributeError:
            return
        else:
            if indent:
                indent_incr, indent_count = indent
                content_handler.characters('\n')
                for i in range(indent_count):
                        content_handler.characters(indent_incr)
            comment(self._content)

    def __repr__(self):
        return 'ecoxipy.pyxom.Comment({})'.format(repr(self._content))


class ProcessingInstruction(XMLNode):
    '''\
    Represent a processing instruction.

    :param target: The processing instruction target.
    :param content: The processing instruction content or :const:`None`.
    '''
    __slots__ = ('_target', '_content')

    def __init__(self, target, content):
        self._target = target
        self._content = content

    @property
    def target(self):
        return self._target

    @property
    def content(self):
        return self._content

    def _create_str(self, out):
        return out.processing_instruction(self._target, self._content)

    def _create_sax_events(self, content_handler, indent):
        if indent:
            indent_incr, indent_count = indent
            content_handler.characters('\n')
            for i in range(indent_count):
                    content_handler.characters(indent_incr)
        content_handler.processingInstruction(self.target,
            u'' if self._content is None else self._content)

    def __repr__(self):
        return 'ecoxipy.pyxom.ProcessingInstruction({}, {})'.format(
            repr(self._target), repr(self._content))


del abc, collections