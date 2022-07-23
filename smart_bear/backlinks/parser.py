from typing import List
from .lexer import EOL, InlineText, lexer, BacklinkPrefix, BacklinkSuffix
from attrs import define
from parsy import *

# MARK: Intermediaries

@define
class Backlink:
    value: str

# MARK: Final Output

@define
class TitleBlock:
    value: str

@define
class BacklinksBlock:
    children: List[InlineText]
    
def checkinstance(Class):
    return test_item(lambda x: isinstance(x, Class), Class.__name__)


backlink_prefix = checkinstance(BacklinkPrefix)
backlink_suffix = checkinstance(BacklinkSuffix)
inline_text = checkinstance(InlineText)

@generate
def backlink():
    yield backlink_prefix
    body: InlineText = yield inline_text
    if body.value[0] == " " or body.value[-1] == " ":
        return fail("backlink must not have space at start or end")
    yield backlink_suffix
    return Backlink(body.value)

eol = checkinstance(EOL)

@generate
def title_block():
    value = yield inline_text.map(lambda x: x.value)
    return (
        string("# ")
        >> any_char.at_least(1).concat().map(TitleBlock)
    ).parse(value)


from .lexer import BacklinksHeading
backlinks_heading = checkinstance(BacklinksHeading)
# TODO: We ned to check for > 2 eol
# lexer needs to tag block breaks like this
backlinks_block = (
    backlinks_heading
    >> (inline_text | eol)
    .until(eol * 2 | eof)
).map(BacklinksBlock)

parser = seq(
    title_block,
    (backlinks_block | inline_text | eol).many(),
)
