from smart_bear.backlinks.lexer import EOL, BacklinksHeading, InlineText
from smart_bear.backlinks.parser import BacklinksBlock, Title, Note
from .lexer import (
    EOL,
    BacklinkPrefix,
    BacklinkSuffix,
    BearID,
    InlineCode,
    InlineText,
    QuoteTick,
)
from smart_bear.backlinks import printer


def test_title():
    given = [Title("abc")]
    expected = "# abc"
    assert printer.title.parse(given) == expected


def test_inline_text():
    given = [InlineText("abc")]
    expected = "abc"
    assert printer.inline_text.parse(given) == expected


def test_eol():
    given = [EOL()]
    expected = "\n"
    assert printer.eol.parse(given) == expected


def test_quote_tick():
    given = [QuoteTick()]
    expected = "`"
    assert printer.quote_tick.parse(given) == expected


def test_inline_code():
    given = [InlineCode()]
    expected = "```"
    assert printer.inline_code.parse(given) == expected


def test_backlinks_heading():
    given = [BacklinksHeading()]
    expected = "## Backlinks"
    assert printer.backlinks_heading.parse(given) == expected


def test_backlink_prefix():
    given = [BacklinkPrefix()]
    expected = "[["
    assert printer.backlink_prefix.parse(given) == expected


def test_backlink_suffix():
    given = [BacklinkSuffix()]
    expected = "]]"
    assert printer.backlink_suffix.parse(given) == expected


def test_bear_id():
    given = [BearID("123")]
    expected = "<!-- {BearID:123} -->"
    assert printer.bear_id.parse(given) == expected


def test_backlinks_block():
    given = [
        BacklinksBlock(
            [
                InlineText("abc"),
                EOL(),
                QuoteTick(),
                InlineCode(),
                BacklinkPrefix(),
            ]
        )
    ]
    expected = "## Backlinks\nabc\n````[["
    assert printer.backlinks_block.parse(given) == expected


def test_note():
    given = [
        Note(
            title=None,
            children=[
                InlineText("test"),
            ],
            bear_id=None,
        )
    ]
    expected = "test\n"
    assert printer.note.parse(given) == expected


def test_note_2():
    given = [
        Note(
            title=Title("abc"),
            children=[
                EOL(),
                InlineText("test"),
            ],
            bear_id=None,
        )
    ]
    expected = "# abc\ntest\n"
    assert printer.note.parse(given) == expected


def test_note_3():
    given = "# abctest"
    from .lexer import token_stream
    from .parser import note

    tokens = token_stream.parse(given)
    assert tokens == [InlineText("# abctest")]
    n = note.parse(tokens)
    assert n == Note(
        title=Title("abctest"),
        children=[],
        bear_id=None,
    )
    # NB: uncertain about this rule but we're ensuring that they always have a new line.
    assert printer.note.parse([n]) == given + "\n"
