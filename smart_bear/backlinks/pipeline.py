from functional import pseq, seq

from smart_bear.backlinks.saved_note_reader import SavedNote
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

        return Note(
            title=note.title,
            children=note.children + [backlinks_block],
            bear_id=note.bear_id,
        )

    from ..console import console
    from rich.text import Text
    from rich.panel import Panel
    from rich.console import Group

    from . import printer

    from . import diff

    (
        seq(saved_notes)
        .map(lambda saved_note: (saved_note, rebuild_note(saved_note.note)))
        .filter(lambda x: x[0].note != x[1])
        .map(lambda x: SavedNote(x[0].url, x[0].raw, x[1]))
        .map(
            lambda saved_note: (
                saved_note.url,
                saved_note.raw,
                printer.note.parse([saved_note.note]),
            )
        )
        .for_each(
            lambda x: console.print(
                Group(
                    Text(x[0], style="bold blue"),
                    Panel(
                        Group(
                            *diff.str_stream(
                                # TODO: inefficient to re-split
                                x[1].split("\n"),
                                x[2].split("\n"),
                            )
                        ),
                    ),
                )
            )
        )
    )
