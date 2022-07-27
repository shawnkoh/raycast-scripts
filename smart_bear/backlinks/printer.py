from smart_bear.backlinks.lexer import ListItemPrefix
from .parser import (
    ListItem,
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
from parsy import generate, eof


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
list_item_prefix = checkinstance(ListItemPrefix).map(lambda x: x.value)


list_item = checkinstance(ListItem).map(
    lambda x: f"{x.prefix.value}{children_unwrapper.many().concat().parse(x.children)}"
)

children_unwrapper = (
    inline_text
    | eol
    | backlink
    | quote_tick
    | inline_code
    | backlinks_heading
    | backlink_prefix
    | backlink_suffix
    | list_item
    | list_item_prefix
)

backlinks_block = (
    checkinstance(EOL).many()
    >> checkinstance(BacklinksBlock)
    .map(lambda x: x.children)
    .map(children_unwrapper.many().concat().parse)
    # TODO: Uncertain if this should append a newline
    # or if we should just wrap the BacklinksHeading and EOL into BacklinksBlock
    .map(lambda x: f"\n\n## Backlinks\n{x}")
)

note_children = (backlinks_block | children_unwrapper).until(
    eol.many() << eof
).concat() << (eol.many() << eof)


# TODO: printer needs a refactor to have a dedicated formatter pipeline
# pritner should only be responsible for reversing parser. nothing more
@generate
def note():
    note: Note = yield checkinstance(Note)

    result = note_children.parse(note.children).rstrip()

    if note.title is not None:
        parsed = title.parse([note.title])
        result = f"{parsed}{result}"
    if note.bear_id is not None:
        parsed = bear_id.parse([note.bear_id])
        result = f"{result}\n\n{parsed}"
    if result[-1:] != "\n":
        result += "\n"
    return result
