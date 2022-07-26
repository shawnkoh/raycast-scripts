from .parser import (
    Note,
    InlineText,
    EOL,
    checkinstance,
    Backlink,
    QuoteTick,
    BacklinkSuffix,
    BacklinkPrefix,
    BacklinksHeading,
    BearID,
    Title,
    BacklinksBlock,
    InlineCode,
)
from parsy import generate


inline_text = checkinstance(InlineText).map(lambda x: x.value)
eol = checkinstance(EOL).result("\n")
backlink = checkinstance(Backlink).map(lambda x: f"[[{x.value}]]")
quote_tick = checkinstance(QuoteTick).result("`")
inline_code = checkinstance(InlineCode).result("```")
backlinks_heading = checkinstance(BacklinksHeading).result("## Backlinks")
backlink_prefix = checkinstance(BacklinkPrefix).result("[[")
backlink_suffix = checkinstance(BacklinkSuffix).result("]]")
bear_id = checkinstance(BearID).map(lambda x: f"<!-- {{BearID:{x.value}}} -->")
title = checkinstance(Title).map(lambda x: f"# {x.value}")

unwrap = (
    inline_text
    | eol
    | backlink
    | quote_tick
    | inline_code
    | backlinks_heading
    | backlink_prefix
    | backlink_suffix
    | bear_id
    | title
)

backlinks_block = (
    checkinstance(BacklinksBlock)
    .map(lambda x: x.children)
    .map(unwrap.many().concat().parse)
    # TODO: Uncertain if this should append a newline
    # or if we should just wrap the BacklinksHeading and EOL into BacklinksBlock
    .map(lambda x: f"## Backlinks\n{x}")
)


# TODO: Uncertain if the note printer should have
@generate
def note():
    note: Note = yield checkinstance(Note)
    _unwrap = (unwrap | backlinks_block).many().concat()
    ls = list(
        filter(lambda x: x is not None, [note.title, *note.children, note.bear_id])
    )
    return f"{_unwrap.parse(ls)}\n"
