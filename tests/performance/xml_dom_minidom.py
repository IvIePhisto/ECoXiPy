from xml.dom import XHTML_NAMESPACE
from xml.dom.minidom import getDOMImplementation


def create_testdoc(_title, _content, _data_count):
    dom_impl = getDOMImplementation()
    #html_doctype = dom_impl.createDocumentType('html', '', '')
    html_doc = dom_impl.createDocument(XHTML_NAMESPACE, 'html', None)
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
        p_element = element('p')
        body_element.appendChild(p_element)
        p_element.setAttribute('data-i', unicode(i))
        p_text = text(unicode(i))
        p_element.appendChild(p_text)
    return html_doc.toxml('UTF-8')
