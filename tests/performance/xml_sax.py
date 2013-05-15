from __future__ import unicode_literals
import sys
if sys.version_info[0] > 2:
    unicode = str

from xml.dom import XHTML_NAMESPACE

from xml.sax.saxutils import XMLGenerator
from xml.sax.xmlreader import AttributesImpl

from io import BytesIO


def create_testdoc(_title, _content, _data_count, _data_text):
    xml_doc = BytesIO()
    try:
        xml_generator = XMLGenerator(xml_doc, 'UTF-8')
        start_element = lambda name, attrs: xml_generator.startElement(name, attrs)
        end_element =  lambda name: xml_generator.endElement(name)
        text = lambda value: xml_generator.characters(value)
        attrs = lambda values: AttributesImpl(values)
        empty_attrs = attrs({})
        xml_generator.startDocument()
        start_element('html', attrs({'xmlns': XHTML_NAMESPACE}))
        start_element('head', empty_attrs)
        start_element('title', empty_attrs)
        text(_title)
        end_element('title')
        end_element('head')
        start_element('body', empty_attrs)
        start_element('h1', empty_attrs)
        text(_title)
        end_element('h1')
        start_element('p', empty_attrs)
        text(_content)
        end_element('p')
        for i in range(_data_count):
            start_element('div', attrs({'data-i': unicode(i)}))
            for j in range(_data_count):
                start_element('p', attrs({'data-j': unicode(j)}))
                text(_data_text)
                end_element('p')
            end_element('div')
        end_element('body')
        end_element('html')
        xml_generator.endDocument()
        return xml_doc.getvalue()
    finally:
        xml_doc.close()


create_testdoc_string = create_testdoc
