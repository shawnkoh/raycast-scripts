import base64
from typing import OrderedDict

import regex
from bs4 import BeautifulSoup
from markdown import Markdown

_markdown_to_html_parser = Markdown()

_bear_id_regex = regex.compile(r"(<!--\s*\{BearID:.+\}\s*-->)")
_title_regex = regex.compile(r"^#(.+)")
_tag_regex = regex.compile(r"\s?(#[\w\/-]+)\s?")
_backlinks_regex = regex.compile(r"## Backlinks\n(.+(\n.)?)+")
_paragraph_regex = regex.compile(r"(?:.+(?:\n.)?)+")
_basic_regex = regex.compile(r"(?m)^Q:\n?((?:.+(?:\n(?!Q:|A:).)?)++)(?:\s*?\n){0,3}(?:^A:\n?((?:.+(?:\n(?!Q:|A:).)?)+))?")
_cloze_regex = regex.compile(r"\{((?>[^{}]|(?R))*)\}")
_cloze_replacer_count = 0

_reference_regex = regex.compile(r"(?i)\s*-*\s*#+\s+References*\s*")
_reference_replacement = "\n\n---\n\n## References\n"

def standardise_references(md: str) -> str:
    return regex.sub(_reference_regex, _reference_replacement, md)

def extract_tag_block(md: str) -> str or None:
    tags = regex.findall(_tag_regex, md)
    # Remove duplicate tags while preserving order
    tags = list(dict.fromkeys(tags))
    if not tags:
        return None
    return "\n".join(tags)

def strip_tags(md: str) -> str:
    """strip all tags and their adjacent whitespaces"""
    return regex.sub(_tag_regex, "", md)

def extract_backlinks(source):
    return regex.findall(_backlinks_regex, source)

def strip_backlinks(source):
    return regex.sub(_backlinks_regex, "", source)

def extract_bear_id(md: str):
    return regex.search(_bear_id_regex, md)

def strip_bear_id(md: str):
    return regex.sub(_bear_id_regex, "", md)

def md_to_basics(source):
    questions = dict()
    for match in regex.finditer(_basic_regex, source):
        question = match[1].strip()
        answer = ""

        if raw_answer := match[2]:
            answer = raw_answer.strip()

        questions[question] = answer
    return questions

def md_to_clozes(source) -> OrderedDict:
    global _cloze_replacer_count
    ordered_dict = OrderedDict()
    for match in regex.finditer(_paragraph_regex, source):
        paragraph = match[0]
        if regex.search(_basic_regex, paragraph) or regex.search(_bear_id_regex, paragraph):
            continue
        _cloze_replacer_count = 0
        stripped_paragraph = regex.sub(_cloze_regex, r"\1", paragraph)
        clozed_paragraph = regex.sub(_cloze_regex, _cloze_replace, paragraph)
        if paragraph == clozed_paragraph:
            continue
        ordered_dict[stripped_paragraph] = clozed_paragraph
    return ordered_dict

def _cloze_replace(match):
    global _cloze_replacer_count
    _cloze_replacer_count += 1
    return f"{{{{c{_cloze_replacer_count}::{match.group(1)}}}}}"

def insert_data(html, attribute, data):
    html_tree = BeautifulSoup(html, 'lxml')
    body = html_tree.body
    if not body:
        return html
    # TODO: not sure why this works, copied from apy
    source_base64 = base64.b64encode(data.encode()).decode()
    body[attribute] = source_base64
    return str(html_tree)

def extract_data(html, attribute):
    html_tree = BeautifulSoup(html, 'lxml')
    body = html_tree.body
    if not body:
        return
    encoded_data = body.get(attribute)
    if encoded_data is None:
        return
    encoded_data = body[attribute]
    if not encoded_data:
        return
    # TODO: Not sure why this works, copied from apy
    encoded_data = encoded_data.encode()
    encoded_data = base64.b64decode(encoded_data).decode()
    return encoded_data

def markdown_to_html(source):
    return _markdown_to_html_parser.reset().convert(source)
