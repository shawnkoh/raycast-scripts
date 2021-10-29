import base64
import re
from typing import OrderedDict

import regex
from bs4 import BeautifulSoup
from markdown import Markdown

import polar_parser

_markdown_to_html_parser = Markdown()

def md_to_basics(source):
    qa_regex = r"Q:\s*((?:(?!A:).+(?:\n|\Z))+)(?:[\S\s]*?)(?:A:\s*((?:(?!Q:).+(?:\n|\Z))+))?"
    questions = dict()
    matches = re.findall(qa_regex, source)
    for match in matches:
        question = match[0].strip()
        question = polar_parser.polar_to_commonmark(question)
        answer = match[1].strip()
        answer = polar_parser.polar_to_commonmark(answer)
        questions[question] = answer
    return questions

def md_to_clozes(source) -> OrderedDict:
    paragraph_regex = r"(?:.+(?:\n.)?)+"
    cloze_regex = r"\{(?>.+?|(?R))*\}"
    paragraphs = re.findall(paragraph_regex, source)
    ordered_dict = OrderedDict()
    for paragraph in paragraphs:
        clozes = regex.findall(cloze_regex, paragraph)
        if not clozes:
            continue
        ordered_dict[paragraph] = clozes
    return ordered_dict


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
