import parsy
from functional import pseq, seq
from .lexer import lexer
from .parser import (
    eol,
    Backlink,
    Note,
    BacklinksBlock,
    EOL,
    InlineText,
    Title,
)
from ..backlinks import parser
from attrs import frozen


@frozen
class Edge:
    from_node: Title
    to_node: Backlink
    children: list[InlineText | EOL | Backlink]


@frozen
class File:
    url: str
    raw: str
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
        note: Note = parser.note.parse(tokens)
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

        return File(url, raw, note, edges)

    files = pseq(urls).map(read).to_list()
    edges_to_node = (
        seq(files)
        .flat_map(lambda file: file.edges)
        .group_by(lambda edge: edge.to_node.value)
        .to_dict()
    )

    def save_note(file: File, note: Note):
        from smart_bear.backlinks import printer

        printed = printer.note.parse([note])
        if file.raw == printed:
            return
        from ..console import console
        from rich.markdown import Markdown
        from rich.console import Group
        from rich.panel import Panel

        console.print(
            Panel(
                Group(
                    Markdown(f"**{file.url}**"),
                    Panel(
                        Markdown(file.raw),
                    ),
                    Panel(
                        Markdown(printed),
                    ),
                )
            )
        )

        # with open(file.url, "w") as f:
        # f.write(printed)

    (
        seq(files)
        .map(lambda x: (x, build_note(edges_to_node, x)))
        .for_each(lambda x: save_note(x[0], x[1]))
    )


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

    if file.note.title is None:
        return Note(
            title=None,
            children=new_children,
            bear_id=file.note.bear_id,
        )

    if file.note.title.value not in edges_to_node:
        return Note(
            file.note.title,
            new_children,
            bear_id=file.note.bear_id,
        )

    edges: list[Edge] = edges_to_node[file.note.title.value]

    def map_edge(edge: Edge):
        return [
            InlineText("* "),
            Backlink(edge.from_node.value),
            EOL(),
            # TODO: i need to fix this
            # the children have to be indented as well.
            InlineText("\t* "),
            *edge.children,
            EOL(),
        ]

    backlinks_block = BacklinksBlock(seq(edges).map(map_edge).flatten().to_list())

    return Note(
        title=file.note.title,
        children=[*new_children, backlinks_block],
        bear_id=file.note.bear_id,
    )
