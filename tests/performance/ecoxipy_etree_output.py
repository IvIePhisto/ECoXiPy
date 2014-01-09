from ecoxipy.etree_output import ETreeOutput
from ecoxipy.decorators import markup_builder_namespace, HTML5_ELEMENT_NAMES
from xml.etree import ElementTree as ET

from tests.performance.ecoxipy_base import create_testdoc


create_testdoc = markup_builder_namespace(
    ETreeOutput, '_b', *HTML5_ELEMENT_NAMES)(create_testdoc)


create_testdoc_string = lambda *args: ET.tostring(create_testdoc(*args).getroot(), 'utf-8')