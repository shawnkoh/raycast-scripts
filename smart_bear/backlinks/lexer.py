from attrs import define
from parsy import any_char, string, eof
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


backlink_prefix = string("[[").result(BacklinkPrefix())
backlink_suffix = string("]]").result(BacklinkSuffix())
quote_tick = string("`").result(QuoteTick())
inline_code = string("```").result(InlineCode())
eol = string("\n").result(EOL())

backlinks_heading = string("## Backlinks\n").map(lambda _: BacklinksHeading())

inline_special = backlink_prefix | backlink_suffix | inline_code | quote_tick | backlinks_heading

# TODO: What about eof?


def _join(ls):
    length = len(ls)

    if length == 1:
        return ls

    # until consume_other=true results in ls[-1] = None
    # for EOF
    if ls[-1] is None:
        return [
            InlineText("".join(ls[:-1]))
        ]

    return [
        InlineText("".join(ls[:-1])),
        ls[-1],
    ]


line = (
    (inline_special | any_char)
    .until(eol | eof, consume_other=True)
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