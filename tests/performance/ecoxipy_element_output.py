from ecoxipy.element_output import ElementOutput
from ecoxipy.decorators import markup_builder_namespace, HTML5_ELEMENT_NAMES

from tests.performance.ecoxipy_base import create_testdoc


create_testdoc = markup_builder_namespace(
    ElementOutput, '_b', *HTML5_ELEMENT_NAMES)(create_testdoc)


create_testdoc_string = lambda *args: bytes(create_testdoc(*args))