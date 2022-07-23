import itertools
from typing import List

import more_itertools
from .lexer import EOL, InlineText, lexer, BacklinkPrefix, BacklinkSuffix
from attrs import define
from parsy import *

# MARK: Intermediaries

@define
class Backlink:
    value: str

    
def checkinstance(Class):
    return test_item(lambda x: isinstance(x, Class), Class.__name__)

backlink_prefix = checkinstance(BacklinkPrefix)
backlink_suffix = checkinstance(BacklinkSuffix)
inline_text = checkinstance(InlineText)

@define
class Line:
    children: List[Backlink | InlineText]


# MARK: Final Output

# TODO: Uncertain if blocks should consume the relevant EOL
# I think, by default we should assume they do.

@define
class TitleBlock:
    value: str

@define
class BacklinksBlock:
    children: List[Line]


@generate
def backlink():
    yield backlink_prefix
    body: InlineText = yield inline_text
    if body.value[0] == " " or body.value[-1] == " ":
        return fail("backlink must not have space at start or end")
    yield backlink_suffix
    return Backlink(body.value)

eol = checkinstance(EOL)

line = (
    (backlink | inline_text)
    .at_least(1)
    .map(Line)
    << (eol | eof)
)

@generate
def title_block():
    value = yield inline_text.map(lambda x: x.value)
    result = (
        string("# ")
        >> any_char
        .at_least(1)
        .concat()
        .map(TitleBlock)
    ).parse(value)
    yield eol | eof
    return result


from .lexer import BacklinksHeading
backlinks_heading = checkinstance(BacklinksHeading)
backlinks_block = (
    backlinks_heading
    >> line
    .until(eol * 2 | eof)
    .map(BacklinksBlock)
)


parser = seq(
    title_block,
    (backlinks_block | line | eol).many(),
).map(lambda x: list(more_itertools.collapse(x)))
