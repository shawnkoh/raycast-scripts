from regex import P

from smart_bear.backlinks.lexer import EOL, InlineText
from smart_bear.backlinks.parser import Backlink, ListItem, ListItemPrefix, Note, Title

from . import edge_builder
from .backlinks_block_builder import Edge


def test_paragraphs():
    given = [
        InlineText("abc"),
    ]

    expected = [
        [InlineText("abc")],
    ]

    assert edge_builder.split_into_paragraphs(given) == expected


def test_paragraphs_2():
    given = [
        InlineText("abc"),
        EOL(),
    ]

    expected = [
        [
            InlineText("abc"),
        ],
    ]

    assert edge_builder.split_into_paragraphs(given) == expected


def test_paragraphs_3():
    given = [
        InlineText("abc"),
        EOL(),
        EOL(),
    ]

    expected = [
        [
            InlineText("abc"),
        ],
    ]

    assert edge_builder.split_into_paragraphs(given) == expected


def test_paragraphs_4():
    given = [
        InlineText("abc"),
        EOL(),
        EOL(),
        InlineText("def"),
    ]

    expected = [
        [
            InlineText("abc"),
        ],
        [
            InlineText("def"),
        ],
    ]

    assert edge_builder.split_into_paragraphs(given) == expected


def test_paragraphs_5():
    given = [
        InlineText("abc"),
        EOL(),
        EOL(),
        InlineText("def"),
        EOL(),
    ]

    expected = [
        [
            InlineText("abc"),
        ],
        [
            InlineText("def"),
        ],
    ]

    assert edge_builder.split_into_paragraphs(given) == expected


def test_paragraphs_6():
    given = [
        InlineText("abc"),
        EOL(),
        EOL(),
        InlineText("def"),
        EOL(),
        EOL(),
    ]

    expected = [
        [
            InlineText("abc"),
        ],
        [
            InlineText("def"),
        ],
    ]

    assert edge_builder.split_into_paragraphs(given) == expected


def test_paragraphs_7():
    given = [
        InlineText("abc"),
        ListItem(
            prefix=ListItemPrefix("* "),
            children=[
                InlineText("def"),
            ],
        ),
    ]

    expected = [
        [
            InlineText("abc"),
        ],
        [
            ListItem(
                prefix=ListItemPrefix("* "),
                children=[
                    InlineText("def"),
                ],
            ),
        ],
    ]

    assert edge_builder.split_into_paragraphs(given) == expected


def test_paragraphs_8():
    given = [
        InlineText("abc"),
        ListItem(
            prefix=ListItemPrefix("* "),
            children=[
                InlineText("def"),
            ],
        ),
        InlineText("ghi"),
    ]

    expected = [
        [
            InlineText("abc"),
        ],
        [
            ListItem(
                prefix=ListItemPrefix("* "),
                children=[
                    InlineText("def"),
                ],
            ),
        ],
        [
            InlineText("ghi"),
        ],
    ]

    assert edge_builder.split_into_paragraphs(given) == expected


def test_paragraphs_9():
    given = [
        ListItem(
            prefix=ListItemPrefix("* "),
            children=[
                InlineText("def"),
            ],
        ),
        EOL(),
        EOL(),
    ]

    expected = [
        [
            ListItem(
                prefix=ListItemPrefix("* "),
                children=[
                    InlineText("def"),
                ],
            ),
        ],
    ]

    assert edge_builder.split_into_paragraphs(given) == expected


def test_paragraphs_10():
    given = [
        ListItem(
            prefix=ListItemPrefix("* "),
            children=[
                InlineText("def"),
            ],
        ),
        InlineText("abc"),
    ]

    expected = [
        [
            ListItem(
                prefix=ListItemPrefix("* "),
                children=[
                    InlineText("def"),
                ],
            ),
        ],
        [
            InlineText("abc"),
        ],
    ]

    assert edge_builder.split_into_paragraphs(given) == expected


def test_paragraphs_11():
    given = [
        ListItem(
            prefix=ListItemPrefix("* "),
            children=[
                InlineText("def"),
            ],
        ),
        EOL(),
        ListItem(
            prefix=ListItemPrefix("* "),
            children=[
                InlineText("def"),
            ],
        ),
        InlineText("abc"),
    ]

    expected = [
        [
            ListItem(
                prefix=ListItemPrefix("* "),
                children=[
                    InlineText("def"),
                ],
            ),
        ],
        [
            ListItem(
                prefix=ListItemPrefix("* "),
                children=[
                    InlineText("def"),
                ],
            ),
        ],
        [
            InlineText("abc"),
        ],
    ]

    assert edge_builder.split_into_paragraphs(given) == expected


def test_paragraphs_12():
    given = [
        ListItem(
            prefix=ListItemPrefix("* "),
            children=[
                InlineText("def"),
            ],
        ),
        EOL(),
        EOL(),
        ListItem(
            prefix=ListItemPrefix("* "),
            children=[
                InlineText("def"),
            ],
        ),
        InlineText("abc"),
    ]

    expected = [
        [
            ListItem(
                prefix=ListItemPrefix("* "),
                children=[
                    InlineText("def"),
                ],
            ),
        ],
        [
            ListItem(
                prefix=ListItemPrefix("* "),
                children=[
                    InlineText("def"),
                ],
            ),
        ],
        [
            InlineText("abc"),
        ],
    ]

    assert edge_builder.split_into_paragraphs(given) == expected


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


def test_build_5():
    given = Note(
        title=Title("Something that links here"),
        children=[
            InlineText(
                "The block of text in the referencing note which contains the link to "
            ),
            Backlink("Sample note"),
            EOL(),
            ListItem(
                prefix=ListItemPrefix("* "), children=[InlineText("Additional line")]
            ),
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
