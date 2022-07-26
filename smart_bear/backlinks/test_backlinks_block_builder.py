from smart_bear.backlinks.lexer import EOL, InlineText, ListItemPrefix
from smart_bear.backlinks.parser import Backlink, BacklinksBlock, Title, ListItem
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
            ListItem(
                prefix=ListItemPrefix("* "),
                children=[
                    Backlink("Something that links here"),
                ],
            ),
            EOL(),
            ListItem(
                prefix=ListItemPrefix("\t* "),
                children=[
                    InlineText(
                        "The block of text in the referencing note which contains the link to "
                    ),
                    Backlink("Sample note"),
                ],
            ),
            EOL(),
        ]
    )

    assert backlinks_block_builder.build(given) == expected


def test_build_2():
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
        ),
        Edge(
            from_node=Title("Something that links here"),
            to_node=Backlink("Sample note"),
            children=[
                InlineText("Another block in that same note which links to "),
                Backlink("Sample note"),
                EOL(),
            ],
        ),
    ]

    expected = BacklinksBlock(
        [
            ListItem(
                prefix=ListItemPrefix("* "),
                children=[
                    Backlink("Something that links here"),
                ],
            ),
            EOL(),
            ListItem(
                prefix=ListItemPrefix("\t* "),
                children=[
                    InlineText(
                        "The block of text in the referencing note which contains the link to "
                    ),
                    Backlink("Sample note"),
                ],
            ),
            EOL(),
            ListItem(
                prefix=ListItemPrefix("\t* "),
                children=[
                    InlineText("Another block in that same note which links to "),
                    Backlink("Sample note"),
                ],
            ),
            EOL(),
        ]
    )

    assert backlinks_block_builder.build(given) == expected


def test_build_3():
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
        ),
        Edge(
            from_node=Title("Not Overthinking"),
            to_node=Backlink("Sample note"),
            children=[
                InlineText("Ali Abdaal"),
                Backlink("Sample note"),
                EOL(),
            ],
        ),
    ]

    expected = BacklinksBlock(
        [
            ListItem(
                prefix=ListItemPrefix("* "),
                children=[
                    Backlink("Something that links here"),
                ],
            ),
            EOL(),
            ListItem(
                prefix=ListItemPrefix("\t* "),
                children=[
                    InlineText(
                        "The block of text in the referencing note which contains the link to "
                    ),
                    Backlink("Sample note"),
                ],
            ),
            EOL(),
            ListItem(
                prefix=ListItemPrefix("* "),
                children=[
                    Backlink("Not Overthinking"),
                ],
            ),
            EOL(),
            ListItem(
                prefix=ListItemPrefix("\t* "),
                children=[
                    InlineText("Ali Abdaal"),
                    Backlink("Sample note"),
                ],
            ),
            EOL(),
        ]
    )

    assert backlinks_block_builder.build(given) == expected


def test_build_4():
    given = []

    expected = None

    assert backlinks_block_builder.build(given) == expected
