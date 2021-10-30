import base64
from typing import OrderedDict

import regex
from bs4 import BeautifulSoup
from markdown import Markdown

import polar_parser

_markdown_to_html_parser = Markdown()

_bear_id_regex = regex.compile(r"\s*(<!--\s*\{BearID:.+\}\s*-->)\s*")
_title_regex = regex.compile(r"^#(.+)")
_paragraph_regex = regex.compile(r"(?:.+(?:\n.)?)+")
_basic_regex = regex.compile(r"(?m)^Q:\n?((?:.+(?:\n(?!Q:|A:).)?)++)(?:\s*?\n){0,3}(?:^A:\n?((?:.+(?:\n(?!Q:|A:).)?)+))?")
_cloze_regex = regex.compile(r"\{((?>[^{}]|(?R))*)\}")
_cloze_replacer_count = 0

def md_to_basics(source):
    questions = dict()
    for match in regex.finditer(_basic_regex, source):
        question = match[1].strip()
        question = polar_parser.polar_to_commonmark(question)
        answer = ""

        if raw_answer := match[2]:
            answer = raw_answer.strip()
            answer = polar_parser.polar_to_commonmark(answer)

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
        stripped_paragraph = polar_parser.polar_to_commonmark(stripped_paragraph)
        clozed_paragraph = polar_parser.polar_to_commonmark(clozed_paragraph)
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
