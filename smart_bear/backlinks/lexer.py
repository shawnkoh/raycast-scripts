from attrs import define
from parsy import any_char, string
import parsy

# Ignore backlinks
# Backlink format

# pass
# [[ok stuff]]

@define
class Text:
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
eol = string("\n")

backlinks_heading = string("## Backlinks\n").map(lambda _: BacklinksHeading())

non_text = backlink_prefix | backlink_suffix | inline_code | quote_tick | backlinks_heading
text = any_char.at_least(1).concat().map(Text)

line = (non_text | text).until(eol | parsy.eof, min=1)

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