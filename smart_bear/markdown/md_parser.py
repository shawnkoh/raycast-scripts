import base64

import regex
import unmarkd
from bs4 import BeautifulSoup

from markdown import Markdown

_markdown_to_html_parser = Markdown()

_bear_id_regex = regex.compile(r"(<!--\s*\{BearID:.+\}\s*-->)")
_title_regex = regex.compile(r"^#\s?(.+)\s*")
_tag_regex = regex.compile(r"\s?(#[\w\/-]+)\s?")
_link_regex = regex.compile(r"\[\[((?>[^\[\]]|(?R))*)\]\]")
_backlinks_regex = regex.compile(r"## Backlinks\n(?:.+(?:\n.)?)+")
_paragraph_regex = regex.compile(r"(?:.+(?:\n.)?)+")
_basic_prompt_regex = regex.compile(r"(?m)^Q:\n?((?:.+(?:\n(?!Q:|A:).)?)++)(?:\s*?\n){0,3}(?:^A:\n?((?:.+(?:\n(?!Q:|A:).)?)+))?")
_cloze_prompt_regex = regex.compile(r"\{((?>[^{}]|(?R))*)\}")

_anki_cloze_regex = regex.compile(r"(\{\{c\d+::((?>[^{}]|(?1))*)\}\})")

_reference_regex = regex.compile(r"(?m)^## References\n(.+(\n.)?)*")

def strip_title(md: str) -> str:
    return regex.sub(_title_regex, "", md)

def strip_references(md: str) -> str:
    return regex.sub(_reference_regex, "", md)

def extract_references(md: str) -> str or None:
    if match := regex.search(_reference_regex, md):
        return match[0]

def extract_tag_block(md: str) -> str or None:
    tags = regex.findall(_tag_regex, md)
    # Remove duplicate tags while preserving order
    tags = list(dict.fromkeys(tags))
    if not tags:
        return None
    return "\n".join(tags)

def is_tag(md: str) -> bool:
    return regex.match(_tag_regex, md) is not None

def contains_tag(md: str, tag: str) -> bool:
    pattern = r"(?<=\S?)#" + tag + r"(?=\S?)"
    return regex.match(pattern, md) is not None

def strip_tags(md: str) -> str:
    """strip all tags and their adjacent whitespaces"""
    return regex.sub(_tag_regex, "", md)

def extract_backlink_blocks(source):
    return regex.findall(_backlinks_regex, source)

def strip_backlink_blocks(source):
    return regex.sub(_backlinks_regex, "", source)

def extract_bear_id(md: str):
    if match := regex.search(_bear_id_regex, md):
        return match[0]

def strip_bear_id(md: str):
    return regex.sub(_bear_id_regex, "", md)

def extract_basic_prompts(source):
    questions = dict()
    for match in regex.finditer(_basic_prompt_regex, source):
        question = match[1].strip()
        answer = ""

        if raw_answer := match[2]:
            answer = raw_answer.strip()

        questions[question] = answer
    return questions

def extract_cloze_prompts(source) -> dict:
    cloze_replacer_count = 0
    def cloze_replace(match):
        nonlocal cloze_replacer_count
        cloze_replacer_count += 1
        return f"{{{{c{cloze_replacer_count}::{match.group(1)}}}}}"

    result = dict()
    for match in regex.finditer(_paragraph_regex, source):
        paragraph = match[0]
        if regex.search(_basic_prompt_regex, paragraph) or regex.search(_bear_id_regex, paragraph):
            continue
        stripped_paragraph = regex.sub(_cloze_prompt_regex, r"\1", paragraph)
        clozed_paragraph = regex.sub(_cloze_prompt_regex, cloze_replace, paragraph)
        if paragraph == clozed_paragraph:
            continue
        result[stripped_paragraph] = clozed_paragraph
    return result

def strip_anki_cloze(md) -> str:
    return regex.sub(md, _anki_cloze_regex, r"\2")

def replace_anki_cloze_with_smart_cloze(md) -> str:
    return regex.sub(md, _anki_cloze_regex, r"{\2}")

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

def html_to_markdown(html):
    return unmarkd.unmark(html)
