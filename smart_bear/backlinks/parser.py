from .lexer import Text, lexer, BacklinkPrefix, BacklinkSuffix
from attrs import define
from parsy import *


def checkinstance(Class):
    return test_item(lambda x: isinstance(x, Class), Class.__name__)

@define
class Title:
    value: str

backlink_prefix = checkinstance(BacklinkPrefix)
backlink_suffix = checkinstance(BacklinkSuffix)
text = checkinstance(Text)

@define
class Backlink:
    value: str

@generate
def backlink():
    yield backlink_prefix
    body: Text = yield text
    if body.value[0] == " " or body.value[-1] == " ":
        return fail("backlink must not have space at start or end")
    yield backlink_suffix
    return Backlink(body.value)

eol = string("\n")

@generate
def title():
    value = yield text.map(lambda x: x.value)
    return (
        string("# ")
        >> any_char.at_least(1).concat().map(Title)
    ).parse(value)

def parse(text: str):
    tokens = lexer.parse(text)
    print(tokens)
