import base64

import unmarkd
from bs4 import BeautifulSoup
from markdown2 import markdown
from parsy import any_char, decimal_digit, string

anki_cloze = (
    string("{{c")
    >> decimal_digit.at_least(1)
    >> string("::")
    >> (string("}}").should_fail("cloze") >> any_char).at_least(1).concat()
    << string("}}")
)


def strip_anki_cloze(md) -> str:
    result = (anki_cloze | any_char).at_least(1).concat().parse(md)
    return result


def replace_anki_cloze_with_smart_cloze(md) -> str:
    result = (
        (anki_cloze.map(lambda x: f"{{{{{x}}}}}") | any_char)
        .at_least(1)
        .concat()
        .parse(md)
    )
    return result


def insert_data(html, attribute, data):
    html_tree = BeautifulSoup(html, "lxml")
    body = html_tree.body
    if not body:
        return html
    # TODO: not sure why this works, copied from apy
    source_base64 = base64.b64encode(data.encode()).decode()
    body[attribute] = source_base64
    return str(html_tree)


def extract_data(html, attribute):
    html_tree = BeautifulSoup(html, "lxml")
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
    return markdown(
        source,
        extras=[
            # "break-on-newline",
            "code-friendly",
            "cuddled-lists",
            "fenced-code-blocks",
            "smarty-pants",
            "strike",
        ],
    )


def html_to_markdown(html):
    return unmarkd.unmark(html)
