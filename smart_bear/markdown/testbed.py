from math import hypot
import parsy
import hypothesis
import hypothesis.strategies

eol = parsy.string("\n")
test = """
I am valid

I am not valid
"""

test2 = "\n\nI am valid!\n\nI am also valid!!"

# trim_end = (parsy.whitespace | parsy.eof).should_fail("trim_end")

# print(trim.parse(test))

test = test.strip()
paragraph_separator = eol.at_least(2)

optional_whitespace = parsy.regex(r"\s*")
non_whitespace = parsy.regex(r"\S")

# Get all the characters that you can as long as you dont hit the marker
# NB: It does not actually dispose the marker.
# CORRECT!
# FIXME: This returns whitespaces at the end of the body
paragraph = non_whitespace + (paragraph_separator.should_fail("paragraph_separator") >> parsy.any_char).many().concat()
paragraphs = paragraph.sep_by(paragraph_separator)

def parse(md):
    md = md.strip()
    return paragraphs.parse(md)

result = parse(test2)
# print(result)

question_prefix = parsy.string("Q:")
answer_prefix = parsy.string("A:")

question = question_prefix >> optional_whitespace >> paragraph
answer = answer_prefix >> optional_whitespace >> paragraph

lbrace = parsy.string("{")
rbrace = parsy.string("}")
string_part = parsy.regex(r"[^\{\}]+")
cloze = lbrace >> optional_whitespace >> string_part << optional_whitespace << rbrace
word = parsy.letter.many().concat()
cloze_or_none = cloze.optional() << word

test = """
Like yeah
I am a {clozed} sentence with multiple { parts like this  }
I am also multiline
"""
# test = test.strip()
# test = "{parts like this }"
# test = "Like A"
# test = "parts like {this} or {that} maybe"

all_cloze = cloze_or_none.sep_by(parsy.whitespace).parse(test)
all_cloze = list(filter(None, all_cloze))
print(all_cloze)

space = parsy.string(" ")
# print(body.sep_by(marker).parse(test2))

# print(parsy.any_char.at_least(1).concat().sep_by(marker).parse(test))
# print(body.sep_by(marker).parse(test))
# print(body.parse_partial(test))
# print(parser.parse_partial(test))


# positive lookahead (does not consume)
# peek()

# negative lookahead (does not consume)
# should_fail()

@hypothesis.given(hypothesis.strategies.text())
def test_cloze(s):
    assert cloze.parse("{" + s + "}") == s