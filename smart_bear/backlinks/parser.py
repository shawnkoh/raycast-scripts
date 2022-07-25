from typing import List, Optional
from rich.pretty import pprint

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
    bear_id: Optional[BearID]

    def to_string(self) -> str:
        unwrap = (
            inline_text.map(lambda x: x.value)
            | eol.result("\n")
            | checkinstance(Backlink).map(lambda x: f"[[{x.value}]]")
            | quote_tick.result("`")
            | inline_code.result("```")
            | backlinks_heading.result("## Backlinks")
            | backlink_prefix.result("[[")
            | backlink_suffix.result("]]")
            | bear_id.map(lambda x: f"<!-- {{BearID:{x.value}}} -->\n")
            | checkinstance(Title).map(lambda x: f"# {x.value}")
        )
        _unwrap = (
            (
                unwrap
                | checkinstance(BacklinksBlock)
                .map(lambda x: x.children)
                .map(lambda x: f"## Backlinks\n{unwrap.many().concat().parse(x)}")
            )
            .many()
            .concat()
        )
        ls = list(
            filter(lambda x: x is not None, [self.title, *self.children, self.bear_id])
        )
        return _unwrap.parse(ls)


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

eol = checkinstance(EOL)


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
    children=(backlinks_block | backlink | any_char).until(
        (bear_id << eol.optional()) | eof
    ),
    bear_id=(bear_id << eol.optional()).optional(),
).combine_dict(Note)
