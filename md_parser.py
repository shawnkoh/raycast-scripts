import re

from hypothesis import given
from hypothesis.strategies import text
from hypothesis.strategies._internal.core import from_regex
from markdown import Markdown

markdown_to_html_parser = Markdown()

def polar_to_commonmark(source):
    source = _replace_polar_bold(source)
    source = _replace_polar_italic(source)
    source = _replace_polar_strikethrough(source)
    # TODO: https://bear.app/faq/Markup%20:%20Markdown/Markdown%20compatibility%20mode/
    # underline
    # line seperator
    # empty checkbox
    # done checkbox
    # unordered lists
    return source

def markdown_to_html(source):
    return markdown_to_html_parser.reset().convert(source)

def _replace_polar_bold(source):
    # *text* to **text**
    bold_pattern = r"(?:\*\*)|(?:\*((?!\*)\S+?(?:[\t ]*?\S)*?)\*)"
    bold_replacement = r"**\1**"
    source = re.sub(bold_pattern, bold_replacement, source)
    return source

def _replace_polar_italic(source):
    # /text/ to *text*
    italic_pattern = r"(?:\/\/)|(?:\/((?!\/)\S+?(?:[\t ]*?\S)*?)\/)"
    italic_replacement = r"*\1*"
    source = re.sub(italic_pattern, italic_replacement, source)
    return source

def _replace_polar_strikethrough(source):
    # -text- to --text--
    # dividers are edge cases of strikethroughs
    divider_pattern = r"(?m)^---$"
    divider_replacement = r"<!DIVIDER!>"
    source = re.sub(divider_pattern, divider_replacement, source)
    strikethrough_pattern = r"(?:--)|(?:-((?!-)\S+?(?:[\t ]*?\S)*?)-)"
    strikethrough_replacement = r"--\1--"
    source = re.sub(strikethrough_pattern, strikethrough_replacement, source)
    source = re.sub(divider_replacement, r"---", source)
    return source

def test_replace_polar_bold():
    valid_sources = ["abc", "", "abc abc", "abc abc abc", "a"]
    invalid_sources = [" abc", "abc ", " ", "\n", "abc\nabc"]
    for source in valid_sources:
        assert _replace_polar_bold(f"*{source}*") == f"**{source}**"
    for source in invalid_sources:
        assert _replace_polar_bold(f"*{source}*") == f"*{source}*"

def test_replace_polar_italic():
    valid_sources = ["abc", "", "abc abc", "abc abc abc", "a"]
    invalid_sources = [" abc", "abc ", " ", "\n", "abc\nabc"]
    for source in valid_sources:
        assert _replace_polar_italic(f"/{source}/") == f"*{source}*"
    for source in invalid_sources:
        assert _replace_polar_italic(f"/{source}/") == f"/{source}/"
        
def test_replace_polar_strikethrough():
    valid_sources = ["abc", "", "abc abc", "abc abc abc", "a"]
    invalid_sources = [" abc", "abc ", " ", "\n", "abc\nabc"]
    for source in valid_sources:
        assert _replace_polar_strikethrough(f"-{source}-") == f"--{source}--"
    for source in invalid_sources:
        assert _replace_polar_strikethrough(f"-{source}-") == f"-{source}-"
