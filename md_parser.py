import re

from hypothesis import *
from markdown import Markdown

markdown_to_html_parser = Markdown()

def polar_to_commonmark(source):
    # *text* to **text**
    bold_pattern = r"(?:\*\*)|(\*(?!\*)\S+?(?:[\t ]*?\S)+?\*)"
    bold_replacement = r"\*\*\1\*\*"
    source = re.sub(bold_pattern, bold_replacement, source)
    source = _replace_polar_italic(source)
    # Strikethrough
    # -text- to --text--
    # dividers are edge cases of strikethroughs
    divider_pattern = r"(?m)^---$"
    divider_replacement = r"<!DIVIDER!>"
    source = re.sub(divider_pattern, divider_replacement, source)
    strikethrough_pattern = r"(?:--)|(-(?!-)\S+?(?:[\t ]*?\S)+?-)"
    strikethrough_replacement = r"--\1--"
    # print(source)
    source = re.sub(strikethrough_pattern, strikethrough_replacement, source)
    source = re.sub(divider_replacement, r"---", source)
    # TODO: https://bear.app/faq/Markup%20:%20Markdown/Markdown%20compatibility%20mode/
    # underline
    # line seperator
    # empty checkbox
    # done checkbox
    # unordered lists
    return source

def _replace_polar_italic(source):
    # /text/ to *text*
    italic_pattern = r"(?:\/\/)|(?:\/(?!\/)(\S+?(?:[\t ]*?\S)+?)\/)"
    italic_replacement = r"*\1*"
    source = re.sub(italic_pattern, italic_replacement, source)
    return source

def markdown_to_html(source):
    return markdown_to_html_parser.reset().convert(source)

hypothesis.given()
def test_replace_polar_italic():
    operator = "/"
    result = "*"
    empty = f""
    word = f"{operator}abc{operator}"
    phrase = f"{operator}abc def ghi{operator}"
    line = f"{phrase}\n"

    assert _replace_polar_italic("/abc/") == "*abc*"
    assert _replace_polar_italic("\n/abc/\n") == "\n*abc*\n"
