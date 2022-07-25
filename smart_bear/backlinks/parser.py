from typing import List, Optional

import more_itertools
from .lexer import (
    EOL,
    BearID,
    InlineCode,
    InlineText,
    QuoteTick,
    BacklinkPrefix,
    BacklinkSuffix,
)
from attrs import frozen
from parsy import *

# MARK: Intermediaries


@frozen
class Backlink:
    value: str


def checkinstance(Class):
    return test_item(lambda x: isinstance(x, Class), Class.__name__)


backlink_prefix = checkinstance(BacklinkPrefix)
backlink_suffix = checkinstance(BacklinkSuffix)
inline_text = checkinstance(InlineText)
quote_tick = checkinstance(QuoteTick)
inline_code = checkinstance(InlineCode)
bear_id = checkinstance(BearID)


# MARK: Final Output

# NB: Blocks should not consume EOLs.
# It makes it difficult to print the original content.
# There's also not much reason to have a Line abstraction.


@frozen
class Title:
    value: str


@frozen
class BacklinksBlock:
    children: List[InlineText | EOL]


@frozen
class Note:
    title: Optional[Title]
    children: List[InlineText | InlineCode | QuoteTick | Backlink | EOL]
    bear_id: BearID


@generate
def backlink():
    yield backlink_prefix
    body: InlineText = yield inline_text
    if body.value[0] == " " or body.value[-1] == " ":
        return fail("backlink must not have space at start or end")
    yield backlink_suffix
    return Backlink(body.value)


from .lexer import BacklinksHeading

backlinks_heading = checkinstance(BacklinksHeading)
inline_special = (
    backlink_prefix
    | backlink_suffix
    | inline_code
    | quote_tick
    | backlinks_heading
    | bear_id
)

eol = checkinstance(EOL)

unwrap = (
    backlink_prefix.result("[[")
    | backlink_suffix.result("]]")
    | quote_tick.result("`")
    | inline_code.result("```")
).map(InlineText)


@generate
def title():
    text = yield inline_text
    value = text.value
    try:
        return (string("# ") >> any_char.at_least(1).concat().map(Title)).parse(value)

    except ParseError:
        return fail("title")


backlinks_block = backlinks_heading >> any_char.until(eol * 2 | eof).map(BacklinksBlock)


parser = seq(
    title=title.optional(),
    children=(
        (backlinks_block | backlink | any_char)
        .until(bear_id)
        .map(lambda x: list(more_itertools.collapse(x)))
    ),
    bear_id=bear_id << eol.optional(),
).combine_dict(Note)
