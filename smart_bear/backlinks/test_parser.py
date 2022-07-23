from pprint import pprint
from smart_bear.backlinks.lexer import EOL, BacklinksHeading
from smart_bear.intelligence.test_utilities import assert_that


def test_title():
    from .parser import title_block, TitleBlock
    from .lexer import InlineText, EOL
    # TODO: Investigate how not to wrap it in an array.
    # The problem is test_item relies on a stream, or at least, a streamable item
    # perhaps we can make text inherit from str? not sure if good idea.
    given = [InlineText("# abc"), EOL()]
    answer = TitleBlock("abc")
    assert(title_block.parse(given)) == answer


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
    from .parser import parser, TitleBlock, BacklinksBlock, Line
    from .lexer import InlineText
    given = [
        InlineText("# Title"),
        EOL(),
        InlineText("## Body"),
        EOL(),
        InlineText("Body"),
        # TODO: This shouldnt be necessary
        EOL(),
    ]
    expected = [
        TitleBlock("Title"),
        Line([InlineText("## Body")]),
        Line([InlineText("Body")]),
    ]
    assert parser.parse(given) == expected
