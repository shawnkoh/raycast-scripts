from tokenize import StringPrefix

import more_itertools
import parsy
from attrs import frozen
from parsy import any_char, eof, string

# Ignore backlinks
# Backlink format

# pass
# [[ok stuff]]


@frozen
class InlineText:
    value: str


@frozen
class BacklinkPrefix:
    pass


@frozen
class BacklinkSuffix:
    pass


@frozen
class InlineCode:
    pass


@frozen
class QuoteTick:
    pass


@frozen
class CodeBlock:
    pass


# ## Backlinks
@frozen
class BacklinksBlockHeader:
    pass


@frozen
class EOL:
    pass


@frozen
class BacklinksHeading:
    pass


@frozen
class Tag:
    value: str


@frozen
class BearID:
    value: str

    def stringify(self) -> str:
        return f"<!-- {{BearID:{self.value}}} -->"


@frozen
class ListItemPrefix:
    value: str


backlink_prefix = string("[[").result(BacklinkPrefix())
backlink_suffix = string("]]").result(BacklinkSuffix())
quote_tick = string("`").result(QuoteTick())
inline_code = string("```").result(InlineCode())
list_item_prefix = (string("* ") | string("- ")).map(ListItemPrefix)


@parsy.generate
def bear_id():
    suffix = string("} -->")
    yield string("<!-- {BearID:")
    # TODO: Uncertain about the | eol | eof
    # need to write tests
    id = yield any_char.until(suffix | eol | eof, min=1).concat()
    yield suffix
    return BearID(id)


eol = string("\n").result(EOL())

tag = (
    string("#").times(min=1, max=1)
    >> string(" ").should_fail("space")
    >> any_char.until(parsy.whitespace).concat().map(Tag)
)

backlinks_heading = string("## Backlinks").result(BacklinksHeading())

inline_special = (
    backlink_prefix
    | backlink_suffix
    | inline_code
    | quote_tick
    | list_item_prefix
    | backlinks_heading
    | tag
    | bear_id
)

# TODO: What about eof?


def _join(ls):
    length = len(ls)

    if length == 1:
        return ls

    return [
        InlineText("".join(ls[:-1])),
        ls[-1],
    ]


# TODO: This can be made much more efficient for sure
# TODO: we should first check for stuff that can only appear at the start of a line.
line = (
    (
        inline_special.until(eol | eof, consume_other=True)
        | any_char.until(inline_special | eol | eof, consume_other=True).map(_join)
    )
    .until(eol | eof, consume_other=True)
    .map(lambda x: list(more_itertools.collapse(x)))
    .map(lambda ls: list(filter(lambda x: x is not None, ls)))
)


token_stream = line.until(eof).map(lambda x: list(more_itertools.collapse(x)))

# TODO: Need to distinct between grammar that short-circuits a paragraph
# and a paragraph.

# fail
# [[ not ok]]
# [[not ok ]]
# [[]]
# backlinks in code block

# lexer
# whitespace ` whitespace
# ```
# [[
# ]]
# whitespace
