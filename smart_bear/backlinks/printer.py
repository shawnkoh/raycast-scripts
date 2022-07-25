from rich.pretty import pprint
import parsy
from functional import seq
from ..backlinks.lexer import lexer
from ..backlinks.parser import (
    parser,
    eol,
    Backlink,
    Note,
    BacklinksBlock,
    EOL,
    InlineText,
    Title,
)
from attrs import frozen


@frozen
class Edge:
    from_title: Title
    to: Backlink
    children: list[InlineText | EOL | Backlink]


@frozen
class File:
    url: str
    note: Note
    edges: list[Edge]


def printer(urls: list[str]):
    def split_into_paragraphs(ls):
        return (
            (
                eol.optional() >> parsy.any_char.until(eol * 2) << (eol * 2)
                | parsy.any_char.map(lambda x: [x])
            )
            .many()
            .parse(ls)
        )

    def read(url):
        raw = _read(url)
        tokens = lexer.parse(raw)
        note: Note = parser.parse(tokens)
        edges = (
            seq([note.children])
            .filter(lambda child: not isinstance(child, BacklinksBlock))
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

        return File(url, note, edges)

    files = seq(urls[:20]).map(read).to_list()
    edge_by_title = (
        seq(files)
        .flat_map(lambda file: file.edges)
        .group_by(lambda edge: edge.to)
        .to_list()
    )
    pprint(edge_by_title)


def _read(url) -> str:
    r = None
    with open(url, "r") as file:
        r = file.read()
        return r
