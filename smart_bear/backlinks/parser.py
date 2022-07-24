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


# MARK: Final Output

# NB: Blocks should not consume EOLs.
# It makes it difficult to print the original content.
# There's also not much reason to have a Line abstraction.

@define
class Title:
    value: str

@define
class BacklinksBlock:
    children: List[InlineText | EOL]


@generate
def backlink():
    yield backlink_prefix
    body: InlineText = yield inline_text
    if body.value[0] == " " or body.value[-1] == " ":
        return fail("backlink must not have space at start or end")
    yield backlink_suffix
    return Backlink(body.value)

eol = checkinstance(EOL)

unwrap = (
    (
        backlink_prefix.result("[[")
        | backlink_suffix.result("]]")
    )
    .map(InlineText)
)

@generate
def title():
    value = yield inline_text.map(lambda x: x.value)
    result = (
        string("# ")
        >> any_char
        .at_least(1)
        .concat()
        .map(Title)
    ).parse(value)
    return result


from .lexer import BacklinksHeading
backlinks_heading = checkinstance(BacklinksHeading)
backlinks_block = (
    backlinks_heading
    >> (inline_text | unwrap | eol)
    .until(eol * 2 | eof)
    .map(BacklinksBlock)
)


parser = seq(
    title,
    (backlinks_block | backlink | inline_text | eol | unwrap).many(),
).map(lambda x: list(more_itertools.collapse(x)))
