from .lexer import *

    
def test_backlinks_heading():
    given = "## Backlinks\n"
    assert backlinks_heading.parse(given) == BacklinksHeading()


