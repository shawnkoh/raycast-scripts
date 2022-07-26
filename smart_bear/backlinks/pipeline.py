import parsy
from functional import pseq, seq

from smart_bear.backlinks.saved_note_reader import SavedNote
from .lexer import token_stream
from .parser import (
    eol,
    Backlink,
    Note,
    BacklinksBlock,
    EOL,
    InlineText,
    Title,
)
from . import parser
from attrs import frozen


def process(urls):
    from .saved_note_reader import read
    from .backlinks_remover import remove_backlinks

    saved_notes: list[SavedNote] = (
        pseq(urls)
        .map(read)
        .map(
            lambda saved_note: SavedNote(
                saved_note.url,
                saved_note.raw,
                remove_backlinks(saved_note.note),
            )
        )
        .to_list()
    )

    from . import edge_builder

    edges_to_node = (
        seq(saved_notes)
        .map(lambda x: x.note)
        .flat_map(edge_builder.build)
        .group_by(lambda edge: edge.to_node.value)
        .to_dict()
    )

    from ..console import console
    from rich.pretty import Pretty

    console.print(Pretty(edges_to_node))
