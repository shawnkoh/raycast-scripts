def test_backlinks_heading():
    from .lexer import backlinks_heading, BacklinksHeading

    given = "## Backlinks"
    expected = BacklinksHeading()
    assert backlinks_heading.parse(given) == expected


def test_line():
    from .lexer import InlineText, line, EOL

    given = "# Title\n"
    expected = [
        InlineText("# Title"),
        EOL(),
    ]
    assert line.parse(given) == expected


def test_line_2():
    from .lexer import InlineText, line

    given = "# Title"
    expected = [InlineText("# Title")]
    assert line.parse(given) == expected


def test_line_3():
    from .lexer import InlineText, line, BacklinkPrefix, BacklinkSuffix

    given = "Some [[Backlink]]"
    expected = [
        InlineText("Some "),
        BacklinkPrefix(),
        InlineText("Backlink"),
        BacklinkSuffix(),
    ]
    assert line.parse(given) == expected


def test_lexer():
    from .lexer import (
        InlineText,
        token_stream,
        BacklinkPrefix,
        BacklinkSuffix,
        EOL,
    )

    given = "# riley_gmi\nAdded to [[ninjacado]] on [[2022-07-19]]."
    expected = [
        InlineText("# riley_gmi"),
        EOL(),
        InlineText("Added to "),
        BacklinkPrefix(),
        InlineText("ninjacado"),
        BacklinkSuffix(),
        InlineText(" on "),
        BacklinkPrefix(),
        InlineText("2022-07-19"),
        BacklinkSuffix(),
        InlineText("."),
    ]
    assert token_stream.parse(given) == expected


def test_list_item_prefix():
    from .lexer import list_item_prefix, ListItemPrefix

    given = "- "
    expected = ListItemPrefix("- ")

    assert list_item_prefix.parse(given) == expected


def test_list_item_prefix_2():
    from .lexer import list_item_prefix, ListItemPrefix

    given = "* "
    expected = ListItemPrefix("* ")

    assert list_item_prefix.parse(given) == expected
