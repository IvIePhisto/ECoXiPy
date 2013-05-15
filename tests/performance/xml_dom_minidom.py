from __future__ import unicode_literals
import sys
if sys.version_info[0] > 2:
    unicode = str

from xml.dom import XHTML_NAMESPACE
from xml.dom.minidom import getDOMImplementation


def create_testdoc(_title, _content, _data_count, _data_text):
    dom_impl = getDOMImplementation()
    html_doctype = dom_impl.createDocumentType('html', None, None)
    html_doc = dom_impl.createDocument(XHTML_NAMESPACE, 'html', html_doctype)
    element = lambda name: html_doc.createElementNS(XHTML_NAMESPACE, name)
    text = lambda value: html_doc.createTextNode(value)
    html_element = html_doc.documentElement
    html_element.setAttribute('xmlns', XHTML_NAMESPACE)
    head_element = element('head')
    html_element.appendChild(head_element)
    title_element = element('title')
    head_element.appendChild(title_element)
    title_text = text(_title)
    title_element.appendChild(title_text)
    body_element = element('body')
    html_element.appendChild(body_element)
    h1_element = element('h1')
    body_element.appendChild(h1_element)
    h1_text = text(_title)
    h1_element.appendChild(h1_text)
    p_element = element('p')
    body_element.appendChild(p_element)
    p_text = text(_content)
    p_element.appendChild(p_text)
    for i in range(_data_count):
        div_element = element('div')
        body_element.appendChild(div_element)
        div_element.setAttribute('data-i', unicode(i))
        for j in range(_data_count):
            p_element = element('p')
            p_element.setAttribute('data-j', unicode(j))
            div_element.appendChild(p_element)
            p_text = text(_data_text)
            p_element.appendChild(p_text)
    return html_doc


def create_testdoc_string(*args):
    html_doc = create_testdoc(*args)
    try:
        return html_doc.toxml('UTF-8')
    finally:
        html_doc.unlink()
