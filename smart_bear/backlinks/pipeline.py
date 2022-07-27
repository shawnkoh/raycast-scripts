from functional import pseq, seq

from smart_bear.backlinks.saved_note_reader import SavedNote
from . import console_representation
from .parser import (
    Note,
)
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
        .filter(lambda x: x.title is not None)
        .flat_map(edge_builder.build)
        .group_by(lambda edge: edge.to_node.value)
        .to_dict()
    )

    def rebuild_note(note: Note) -> Note:
        from . import backlinks_block_builder

        if note.title is None or note.title.value not in edges_to_node:
            return note

        edges = edges_to_node[note.title.value]
        backlinks_block = backlinks_block_builder.build(edges)
        if backlinks_block is None:
            return note

        return Note(
            title=note.title,
            children=note.children + [backlinks_block],
            bear_id=note.bear_id,
        )

    from ..console import console

    (
        seq(saved_notes)
        .map(lambda saved_note: (saved_note, rebuild_note(saved_note.note)))
        .filter(lambda x: x[0].note != x[1])
        .map(lambda x: SavedNote(x[0].url, x[0].raw, x[1]))
        .map(console_representation.saved_note)
        .for_each(console.print)
    )
