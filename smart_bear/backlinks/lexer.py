from attrs import define
from parsy import any_char, string, eof
import parsy
import more_itertools

# Ignore backlinks
# Backlink format

# pass
# [[ok stuff]]


@define
class InlineText:
    value: str


@define
class BacklinkPrefix:
    pass


@define
class BacklinkSuffix:
    pass


@define
class InlineCode:
    pass


@define
class QuoteTick:
    pass


@define
class CodeBlock:
    pass


# ## Backlinks
@define
class BacklinksBlockHeader:
    pass


@define
class EOL:
    pass


@define
class BacklinksHeading:
    pass


backlink_prefix = string("[[").result(BacklinkPrefix())
backlink_suffix = string("]]").result(BacklinkSuffix())
quote_tick = string("`").result(QuoteTick())
inline_code = string("```").result(InlineCode())
eol = string("\n").result(EOL())

backlinks_heading = string("## Backlinks").result(BacklinksHeading())

inline_special = (
    backlink_prefix | backlink_suffix | inline_code | quote_tick | backlinks_heading
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
line = (
    (
        inline_special.until(eol | eof, consume_other=True)
        | any_char.until(inline_special | eol | eof, consume_other=True).map(_join)
    )
    .until(eol | eof, consume_other=True)
    .map(lambda x: list(more_itertools.collapse(x)))
    .map(lambda ls: list(filter(lambda x: x is not None, ls)))
)


lexer = line.until(eof).map(lambda x: list(more_itertools.collapse(x)))

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
