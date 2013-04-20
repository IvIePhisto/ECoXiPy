from xml.dom import XHTML_NAMESPACE

from ecoxipy.dom_output import DOMOutput
from ecoxipy.decorators import markup_builder_namespace


@markup_builder_namespace(DOMOutput, '_b', 'html', 'head', 'title', 'body', 'h1', 'p')
def create_testdoc(_title, _content, _data_count):
    return html(
            head(
                title(_title)
            ),
            body(
                h1(_title),
                p(_content),
                (p({'data-i': i}, i) for i in range(_data_count))
            ),
            xmlns=XHTML_NAMESPACE
        ).toxml('UTF-8')

