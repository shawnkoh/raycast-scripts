from hypothesis import given
from smart_bear.intelligence.test_utilities import assert_that


def test_title():
    from .parser import title, Title
    from .lexer import Text
    # TODO: Investigate how not to wrap it in an array.
    # The problem is test_item relies on a stream, or at least, a streamable item
    # perhaps we can make text inherit from str? not sure if good idea.
    given = [Text("# abc")]
    answer = Title("abc")
    assert(title.parse(given)) == answer


def test_backlink():
    from .parser import backlink, Backlink, BacklinkPrefix, BacklinkSuffix
    from .lexer import Text

    given = [BacklinkPrefix(), Text("abc"), BacklinkSuffix()]
    assert_that(backlink.parse(given), Backlink("abc"))
