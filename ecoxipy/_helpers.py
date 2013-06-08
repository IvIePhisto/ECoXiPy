# -*- coding: utf-8 -*-

from ecoxipy import XMLWellFormednessException


def _prepare_value(value):
    return value.encode('unicode-escape').decode().replace('"', '\\"')


def _xml_name_regex():
    import re
    name_start_char = u':|[A-Z]|_|[a-z]|[\xC0-\xD6]|[\xD8-\xF6]|[\xF8-\u02FF]|[\u0370-\u037D]|[\u037F-\u1FFF]|[\u200C-\u200D]|[\u2070-\u218F]|[\u2C00-\u2FEF]|[\u3001-\uD7FF]|[\uF900-\uFDCF]|[\uFDF0-\uFFFD]'
    extented_chars_start = '\U00010000'
    extented_chars_end = '\U000EFFFF'
    if len(extented_chars_start) > 1: # narrow Python build
        name_start_char = u'{}|[{}-{}][{}-{}]'.format(name_start_char,
            extented_chars_start[0], extented_chars_end[0],
            extented_chars_start[1], extented_chars_end[1],)
    else: # wide Python build
        name_start_char = u'{}|[{}-{}]'.format(name_start_char,
            extented_chars_start, extented_chars_end)
    name_char = u'{}|\\-|\\.|[0-9]|\xB7|[\u0300-\u036F]|[\u203F-\u2040]'.format(name_start_char)
    name = u'^{}({})*$'.format(name_start_char, name_char)
    name_regex = re.compile(name)
    return name_regex
_xml_name_regex = _xml_name_regex()


def enforce_valid_xml_name(value):
    if _xml_name_regex.match(value) is None:
        raise XMLWellFormednessException(
            u'The value "{}" is not a valid XML name.'.format(_prepare_value(value)))


def enforce_valid_pi_target(value):
    if _xml_name_regex.match(value) is None or value.lower() == u'xml':
        raise XMLWellFormednessException(
            u'The value "{}" is not a valid XML processing instruction target.'.format(_prepare_value(value)))


def enforce_valid_pi_content(value):
    if u'?>' in value:
        raise XMLWellFormednessException(
            u'The value "{}" is not a valid XML processing instruction content because it contains "?>".'.format(_prepare_value(value)))


def enforce_valid_comment(value):
    if u'--' in value:
        raise XMLWellFormednessException(
            u'The value "{}" is not a valid XML comment because it contains "--".'.format(_prepare_value(value)))

def enforce_valid_doctype_systemid(value):
    if u'"' in value and u"'" in value:
        raise XMLWellFormednessException(
            u'The value "{}" is not a valid document type system ID.'.format(_prepare_value(value)))


def _doctype_publicid_regex():
    import re
    return re.compile(u'^[\x20\x0D\x0A]|[a-zA-Z0-9]|[\\-\'\\(\\)\\+,\\./:=\\?;\\!\\*\\#@\\$_%]$')
_doctype_publicid_regex = _doctype_publicid_regex()


def enforce_valid_doctype_publicid(value):
    if _doctype_publicid_regex.match(value) is None:
        raise XMLWellFormednessException(
            u'The value "{}" is not a valid document type public ID.'.format(_prepare_value(value)))


def get_qualified_name_components(name):
    components = name.split(u':', 1)
    if len(components) == 1:
        prefix = None
        local_name = name
    else:
        prefix, local_name = components
        if u':' in local_name:
            prefix = None
            local_name = name
    return prefix, local_name


def inherit_docstring(base):
    def decorator(attr):
        name = attr.__name__
        if attr.__doc__ is None:
            try:
                original_attr = getattr(base, name)
            except AttributeError:
                pass
            else:
                original_doc = original_attr.__doc__
                if original_doc is not None:
                    attr.__doc__ = original_doc
        return attr
    return decorator
