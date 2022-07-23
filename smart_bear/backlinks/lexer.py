from attrs import define
from parsy import any_char, string
import parsy

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


backlink_prefix = string("[[").map(lambda _: BacklinkPrefix())
backlink_suffix = string("]]").map(lambda _: BacklinkSuffix())
quote_tick = string("`").map(lambda _: QuoteTick())
inline_code = string("```").map(lambda _: InlineCode())
eol = string("\n").result(EOL())

backlinks_heading = string("## Backlinks\n").map(lambda _: BacklinksHeading())

inline_special = backlink_prefix | backlink_suffix | inline_code | quote_tick | backlinks_heading

# TODO: What about eof?


def _join(ls):
    length = len(ls)

    if length == 1:
        return ls

    return [
        InlineText("".join(ls[:-1])),
        ls[-1],
    ]


line = (
    any_char
    .until(inline_special | eol, consume_other=True)
    .map(_join)
)

lexer = line.many()

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