from smart_bear.backlinks.lexer import EOL, InlineText
from smart_bear.backlinks.parser import Backlink, Title, Note
from . import edge_builder
from .backlinks_block_builder import Edge


def test_build():
    given = Note(
        title=Title("Something that links here"),
        children=[
            InlineText(
                "The block of text in the referencing note which contains the link to "
            ),
            Backlink("Sample note"),
            EOL(),
        ],
        bear_id=None,
    )

    expected = [
        Edge(
            from_node=Title("Something that links here"),
            to_node=Backlink("Sample note"),
            children=[
                InlineText(
                    "The block of text in the referencing note which contains the link to "
                ),
                Backlink("Sample note"),
                EOL(),
            ],
        )
    ]

    from ..console import console
    from rich.pretty import Pretty

    console.print(Pretty(edge_builder.build(given)))
    console.print(Pretty(expected))

    assert edge_builder.build(given) == expected
