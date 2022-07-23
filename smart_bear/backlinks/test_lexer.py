from .lexer import *
import hypothesis

    
def test_backlinks_heading():
    given = "## Backlinks\n"
    assert backlinks_heading.parse(given) == BacklinksHeading()


