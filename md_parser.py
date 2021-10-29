import base64
import re
from typing import OrderedDict

import regex
from bs4 import BeautifulSoup
from markdown import Markdown

import polar_parser

_markdown_to_html_parser = Markdown()

_bear_id_regex = r"\s*(<!--\s*\{BearID:.+\}\s*-->)\s*"
_paragraph_regex = r"(?:.+(?:\n.)?)+"
_basic_regex = r"Q:\s*((?:(?!A:).+(?:\n|\Z))+)(?:[\S\s]*?)(?:A:\s*((?:(?!Q:).+(?:\n|\Z))+))?"
_cloze_regex = r"\{((?>[^{}]|(?R))*)\}"
_cloze_replacer_count = 0

def md_to_basics(source):
    questions = dict()
    matches = re.findall(_basic_regex, source)
    for match in matches:
        question = match[0].strip()
        question = polar_parser.polar_to_commonmark(question)
        answer = match[1].strip()
        answer = polar_parser.polar_to_commonmark(answer)
        questions[question] = answer
    return questions

def md_to_clozes(source) -> OrderedDict:
    global _cloze_replacer_count
    source = re.sub(_bear_id_regex, "", source)
    paragraphs = re.findall(_paragraph_regex, source)
    ordered_dict = OrderedDict()
    for paragraph in paragraphs:
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
    encoded_data = body[attribute]
    if not encoded_data:
        return
    # TODO: Not sure why this works, copied from apy
    encoded_data = encoded_data.encode()
    encoded_data = base64.b64decode(encoded_data).decode()
    return encoded_data

def markdown_to_html(source):
    return _markdown_to_html_parser.reset().convert(source)
