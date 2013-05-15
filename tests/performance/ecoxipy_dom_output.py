from ecoxipy.dom_output import DOMOutput
from ecoxipy.decorators import markup_builder_namespace, HTML5_ELEMENT_NAMES

from tests.performance.ecoxipy_base import create_testdoc


create_testdoc = markup_builder_namespace(
    DOMOutput, '_b', *HTML5_ELEMENT_NAMES)(create_testdoc)


def create_testdoc_string(*args):
    html_doc = create_testdoc(*args)
    try:
        return html_doc.toxml('UTF-8')
    finally:
        html_doc.unlink()