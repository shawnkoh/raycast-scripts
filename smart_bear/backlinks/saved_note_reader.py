from .lexer import token_stream
from .parser import (
    Note,
)
from . import parser
from attrs import frozen


@frozen
class SavedNote:
    url: str
    raw: str
    note: Note


def read(url):
    raw: str
    with open(url, "r") as file:
        raw = file.read()

    tokens = token_stream.parse(raw)
    note: Note = parser.note.parse(tokens)

    return SavedNote(url, raw, note)
