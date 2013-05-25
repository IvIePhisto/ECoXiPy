# -*- coding: utf-8 -*-
def _xml_name_regex():
    import re
    name_start_char = u':|[A-Z]|_|[a-z]|[\xC0-\xD6]|[\xD8-\xF6]|[\xF8-\u02FF]|[\u0370-\u037D]|[\u037F-\u1FFF]|[\u200C-\u200D]|[\u2070-\u218F]|[\u2C00-\u2FEF]|[\u3001-\uD7FF]|[\uF900-\uFDCF]|[\uFDF0-\uFFFD]|[\U00010000-\U000EFFFF]'
    name_char = u'{}|\\-|\\.|[0-9]|\xB7|[\u0300-\u036F]|[\u203F-\u2040]'.format(name_start_char)
    name = u'^{}({})*$'.format(name_start_char, name_char)
    name_regex = re.compile(name)
    return name_regex

_xml_name_regex = _xml_name_regex()


class XMLWellFormednessException(Exception):
    '''Indicates XML is not well-formed.'''


def enforce_valid_xml_name(value):
    if _xml_name_regex.match(value) is None:
        raise XMLWellFormednessException(
            u'The value "{}" is not a valid XML name.'.format(value))


def enforce_valid_pi_target(value):
    if _xml_name_regex.match(value) is None or value.lower() == u'xml':
        raise XMLWellFormednessException(
            u'The value "{}" is not a valid XML processing instruction target.'.format(value))


def enforce_valid_pi_content(value):
    if u'?>' in value:
        raise XMLWellFormednessException(
            u'The value "{}" is not a valid XML processing instruction content because it contains "?>".'.format(value))


def enforce_valid_comment(value):
    if u'--' in value:
        raise XMLWellFormednessException(
            u'The value "{}" is not a valid XML comment because it contains "--".'.format(value))
