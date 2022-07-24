def test_backlinks_heading():
    from .lexer import backlinks_heading, BacklinksHeading
    given = "## Backlinks\n"
    assert backlinks_heading.parse(given) == BacklinksHeading()


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
