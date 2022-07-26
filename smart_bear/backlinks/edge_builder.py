import parsy
from functional import seq
from .parser import (
    eol,
    Backlink,
    Note,
    EOL,
    InlineText,
    Title,
)
from attrs import frozen


@frozen
class Edge:
    from_node: Title
    to_node: Backlink
    children: list[InlineText | EOL | Backlink]


def build(note: Note) -> list[Edge]:
    return (
        seq([note.children])
        .flat_map(split_into_paragraphs)
        .filter(lambda x: any(isinstance(ele, Backlink) for ele in x))
        .filter(lambda x: len(x) > 0)
        .flat_map(
            lambda paragraph: (
                seq(paragraph)
                .filter(lambda x: isinstance(x, Backlink))
                .map(lambda backlink: Edge(note.title, backlink, paragraph))
            )
        )
        .to_list()
    )


def split_into_paragraphs(ls):
    return (
        (
            eol.optional() >> parsy.any_char.until(eol * 2) << (eol * 2)
            | parsy.any_char.map(lambda x: [x])
        )
        .many()
        .parse(ls)
    )
