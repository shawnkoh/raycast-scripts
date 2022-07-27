from smart_bear.backlinks.saved_note_reader import SavedNote
from smart_bear.backlinks import printer
from rich.console import Group
from rich.panel import Panel
from rich.text import Text

from . import diff


def saved_note(saved_note: SavedNote):
    new_raw = printer.note.parse([saved_note.note])
    return Group(
        Text(saved_note.url, style="bold blue"),
        Panel(
            Group(
                *diff.str_stream(
                    # TODO: inefficient to re-split
                    saved_note.raw.split("\n"),
                    new_raw.split("\n"),
                )
            ),
        ),
    )
