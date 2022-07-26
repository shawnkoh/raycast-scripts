from smart_bear.backlinks.lexer import EOL, InlineText
from smart_bear.backlinks.parser import Backlink, BacklinksBlock, Title
from . import backlinks_block_builder
from .backlinks_block_builder import Edge


def test_build():
    given = [
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

    expected = BacklinksBlock(
        [
            InlineText("* "),
            Backlink("Something that links here"),
            EOL(),
            InlineText("\t* "),
            InlineText(
                "The block of text in the referencing note which contains the link to "
            ),
            Backlink("Sample note"),
            EOL(),
        ]
    )

    assert backlinks_block_builder.build(given) == expected
