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

    assert edge_builder.build(given) == expected


def test_build_2():
    given = Note(
        title=Title("Something that links here"),
        children=[
            InlineText(
                "The block of text in the referencing note which contains the link to "
            ),
            Backlink("Sample note"),
            EOL(),
            InlineText("Additional line"),
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
                InlineText("Additional line"),
            ],
        )
    ]

    assert edge_builder.build(given) == expected


def test_build_3():
    given = Note(
        title=Title("Something that links here"),
        children=[
            InlineText(
                "The block of text in the referencing note which contains the link to "
            ),
            Backlink("Sample note"),
            EOL(),
            InlineText("Additional line"),
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
                InlineText("Additional line"),
                EOL(),
            ],
        )
    ]

    assert edge_builder.build(given) == expected


def test_build_4():
    given = Note(
        title=Title("Something that links here"),
        children=[
            InlineText(
                "The block of text in the referencing note which contains the link to "
            ),
            Backlink("Sample note"),
            EOL(),
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
            ],
        )
    ]

    assert edge_builder.build(given) == expected
