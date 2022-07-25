from pprint import pprint

import pytest
from smart_bear.backlinks.lexer import EOL, BacklinksHeading, InlineText
from smart_bear.backlinks.parser import Title
from smart_bear.intelligence.test_utilities import assert_that
from .lexer import EOL, BearID, InlineText
from .parser import parser
import parsy


def test_title():
    from .parser import title
    from .lexer import InlineText, EOL

    # TODO: Investigate how not to wrap it in an array.
    # The problem is test_item relies on a stream, or at least, a streamable item
    # perhaps we can make text inherit from str? not sure if good idea.
    given = [InlineText("# abc")]
    expected = Title("abc")
    assert (title.parse(given)) == expected


def test_title_or_inline_text():
    from .parser import title, inline_text
    from .lexer import InlineText

    given = [InlineText("abc")]
    expected = InlineText("abc")
    assert ((title | inline_text).parse(given)) == expected


def test_title_optional():
    from .parser import title
    from .lexer import InlineText

    given = [InlineText("abc")]
    assert title.optional().parse_partial(given)[0] is None
    # NB: this does not work because a failed parse does not consume the stream
    with pytest.raises(parsy.ParseError):
        title.optional().parse(given)


def test_backlink():
    from .parser import backlink, Backlink, BacklinkPrefix, BacklinkSuffix

    given = [BacklinkPrefix(), InlineText("abc"), BacklinkSuffix()]
    assert_that(backlink.parse(given), Backlink("abc"))


def test_backlinks_block():
    from .parser import BacklinksBlock, backlinks_block

    inline_text = InlineText("some backlink")
    given = [
        BacklinksHeading(),
        EOL(),
        inline_text,
    ]
    expected = BacklinksBlock(
        [
            EOL(),
            inline_text,
        ]
    )

    assert backlinks_block.parse(given) == expected


def test_backlinks_block_2():
    from .parser import BacklinksBlock, backlinks_block

    inline_text = InlineText("some backlink")
    given = [
        BacklinksHeading(),
        EOL(),
        inline_text,
        EOL(),
    ]
    expected = BacklinksBlock(
        [
            EOL(),
            inline_text,
            EOL(),
        ]
    )

    assert backlinks_block.parse(given) == expected


def test_parser():
    from .parser import Title, Note

    given = [
        InlineText("# Title"),
        EOL(),
        BearID("1234"),
    ]
    expected = Note(
        title=Title("Title"),
        children=[
            EOL(),
        ],
        bear_id=BearID("1234"),
    )
    assert parser.parse(given) == expected


def test_parser_1():
    from .parser import Title, Note

    given = [
        InlineText("# Title"),
        EOL(),
        InlineText("## Body"),
        EOL(),
        InlineText("Body"),
        BearID("1234"),
    ]
    expected = Note(
        title=Title("Title"),
        children=[
            EOL(),
            InlineText("## Body"),
            EOL(),
            InlineText("Body"),
        ],
        bear_id=BearID("1234"),
    )
    assert parser.parse(given) == expected


def test_parser_2():
    from .parser import Title, Note

    given = [
        InlineText("# Title"),
        EOL(),
        InlineText("## Body"),
        EOL(),
        InlineText("Body"),
        EOL(),
        BearID("1234"),
    ]
    expected = Note(
        title=Title("Title"),
        children=[
            EOL(),
            InlineText("## Body"),
            EOL(),
            InlineText("Body"),
            EOL(),
        ],
        bear_id=BearID("1234"),
    )
    assert parser.parse(given) == expected


def test_parser_3():
    from .lexer import lexer
    from .parser import Note

    given = "# Executive functions are actions towards self-regulation, per Barkley\n<!-- {BearID:1234} -->"

    expected = Note(
        title=Title(
            "Executive functions are actions towards self-regulation, per Barkley"
        ),
        children=[EOL()],
        bear_id=BearID("1234"),
    )
    assert parser.parse(lexer.parse(given)) == expected
