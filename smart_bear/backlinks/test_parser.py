from pprint import pprint
from smart_bear.backlinks.lexer import EOL, BacklinksHeading, InlineText
from smart_bear.backlinks.parser import Title
from smart_bear.intelligence.test_utilities import assert_that


def test_title():
    from .parser import title 
    from .lexer import InlineText, EOL
    # TODO: Investigate how not to wrap it in an array.
    # The problem is test_item relies on a stream, or at least, a streamable item
    # perhaps we can make text inherit from str? not sure if good idea.
    given = [InlineText("# abc")]
    answer = Title("abc")
    assert(title.parse(given)) == answer


def test_backlink():
    from .parser import backlink, Backlink, BacklinkPrefix, BacklinkSuffix
    from .lexer import InlineText

    given = [BacklinkPrefix(), InlineText("abc"), BacklinkSuffix()]
    assert_that(backlink.parse(given), Backlink("abc"))


def test_backlinks_block():
    from .parser import BacklinksBlock, backlinks_block, Line
    from .lexer import InlineText
    inline_text = InlineText("some backlink")
    given = [BacklinksHeading(), inline_text, EOL()]
    expected = BacklinksBlock([Line([inline_text])])

    assert backlinks_block.parse(given) == expected

def test_parser():
    from .parser import parser, Title, BacklinksBlock, Line
    from .lexer import InlineText
    given = [
        InlineText("# Title"),
        EOL(),
    ]
    expected = [
        Title("Title"),
        EOL(),
    ]
    assert parser.parse(given) == expected

def test_parser_1():
    from .parser import parser, Title, BacklinksBlock, Line
    from .lexer import InlineText
    given = [
        InlineText("# Title"),
        EOL(),
        InlineText("## Body"),
        EOL(),
        InlineText("Body"),
    ]
    expected = [
        Title("Title"),
        EOL(),
        Line([InlineText("## Body")]),
        Line([InlineText("Body")]),
    ]
    assert parser.parse(given) == expected


def test_parser_2():
    from .parser import parser, Title, BacklinksBlock, Line
    from .lexer import InlineText
    given = [
        InlineText("# Title"),
        EOL(),
        InlineText("## Body"),
        EOL(),
        InlineText("Body"),
        EOL(),
    ]
    expected = [
        Title("Title"),
        EOL(),
        Line([InlineText("## Body")]),
        Line([InlineText("Body")]),
    ]
    assert parser.parse(given) == expected

def test_parser_3():
    from .lexer import lexer
    from .parser import parser
    given = "# Executive functions are actions towards self-regulation, per Barkley"

    expected = [
        Title("Executive functions are actions towards self-regulation, per Barkley"),
    ]
    assert parser.parse(lexer.parse(given)) == expected
