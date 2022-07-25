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
    from_node: Title
    to_node: Backlink
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

    files = seq(urls[:50]).map(read).to_list()
    edges_to_node = (
        seq(files)
        .flat_map(lambda file: file.edges)
        .group_by(lambda edge: edge.to_node.value)
        .to_dict()
    )

    (
        seq(files)
        .filter(lambda file: file.note.title.value in edges_to_node)
        .map(lambda x: build_note(edges_to_node, x))
        .peek(pprint)
        .to_list()
    )
    # pprint(edges_to_node)


def _read(url) -> str:
    r = None
    with open(url, "r") as file:
        r = file.read()
    return r


def build_note(edges_to_node, file: File):
    new_children = (
        seq(file.note.children)
        .filter(lambda child: not isinstance(child, BacklinksBlock))
        .to_list()
    )

    if file.note.title.value not in edges_to_node:
        return Note(file.note.title, new_children)
    else:
        edges: list[Edge] = edges_to_node[file.note.title.value]

        def map_edge(edge: Edge):
            return [
                InlineText("* "),
                Backlink(edge.from_node.value),
                EOL(),
                InlineText("\t* "),
                EOL(),
                *edge.children,
            ]

        backlinks_block = (
            BacklinksBlock(seq(edges).map(map_edge).flatten().to_list()),
        )

        return Note(
            title=file.note.title,
            children=[*new_children, *backlinks_block],
            bear_id=file.note.bear_id,
        )
