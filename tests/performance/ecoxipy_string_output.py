from ecoxipy.string_output import StringOutput
from ecoxipy.decorators import markup_builder_namespace, HTML5_ELEMENT_NAMES

from tests.performance.ecoxipy_base import create_testdoc

create_testdoc = markup_builder_namespace(
    StringOutput, '_b', *HTML5_ELEMENT_NAMES)(create_testdoc)

create_testdoc_string = lambda *args: create_testdoc(*args).encoded
