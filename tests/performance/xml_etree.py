from xml.etree import ElementTree as ET
from xml.dom import XHTML_NAMESPACE

import sys
if sys.version_info[0] > 2:
    unicode = str

def create_testdoc(_title, _content, _data_count, _data_text):
    html_element = ET.Element('html', xmlns=XHTML_NAMESPACE)
    head_element = ET.Element('head')
    html_element.append(head_element)
    title_element = ET.Element('title')
    title_element.text = _title
    head_element.append(title_element)
    body_element = ET.Element('body')
    html_element.append(body_element)
    h1_element = ET.Element('h1')
    h1_element.text = _title
    body_element.append(h1_element)
    p_element = ET.Element('p')
    p_element.text = _content
    body_element.append(p_element)
    for i in range(_data_count):
        div_element = ET.Element('div', {'data-i': unicode(i)})
        body_element.append(div_element)
        for j in range(_data_count):
            p_element = ET.Element('p', {'data-j': unicode(j)})
            p_element.text = _data_text
            div_element.append(p_element)
    html_doc = ET.ElementTree(html_element)
    return html_doc


create_testdoc_string = lambda *args: ET.tostring(
    create_testdoc(*args).getroot(), 'utf-8')