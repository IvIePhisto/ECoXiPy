from xml.dom import XHTML_NAMESPACE

from ecoxipy.string_output import StringOutput
from ecoxipy.decorators import markup_builder_namespace, HTML5_ELEMENT_NAMES

@markup_builder_namespace(StringOutput, '_b', *HTML5_ELEMENT_NAMES)
def create_testdoc(_title, _content, _data_count, _data_text):
    return _b[:'html'] (
        html(
            head(
                title(_title)
            ),
            body(
                h1(_title),
                p(_content),
                (p({'data-i': i}, (
                        p({'data-j': j}, _data_count)
                        for j in range(_data_count)))
                    for i in range(_data_count))
            ),
            xmlns=XHTML_NAMESPACE
        )
    )

