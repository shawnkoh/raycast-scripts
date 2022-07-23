from hypothesis import given
from smart_bear.backlinks.lexer import BacklinksHeading
from smart_bear.intelligence.test_utilities import assert_that


def test_title():
    from .parser import title, Title
    from .lexer import InlineText
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
    from .parser import BacklinksBlock, backlinks_block
    from .lexer import InlineText
    inline_text = InlineText("some backlink")
    given = [BacklinksHeading(), inline_text]
    expected = BacklinksBlock([inline_text])

    assert backlinks_block.parse(given) == expected