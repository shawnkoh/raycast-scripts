from rich.console import Group
from rich.panel import Panel
from rich.text import Text

from . import diff


def saved_note(url, raw, new_raw):
    return Group(
        Text(url, style="bold blue"),
        Panel(str_diff(raw, new_raw)),
    )


def str_diff(before: str, after: str):
    return Group(
        *diff.str_stream(
            # TODO: inefficient to re-split
            before.split("\n"),
            after.split("\n"),
        )
    )
