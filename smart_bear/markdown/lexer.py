from attrs import define
from parsy import string, whitespace, eof, peek, any_char


@define
class Separator:
    raw_value: str


@define
class QuestionPrefix:
    raw_value: str


@define
class AnswerPrefix:
    raw_value: str


@define
class LeftBrace:
    raw_value: str


@define
class RightBrace:
    raw_value: str


@define
class Text:
    raw_value: str


@define
class Break:
    raw_value: str


# Utilities
eol = string("\n").map(Break)
flatten_list = lambda ls: sum(ls, [])
exclude_none = lambda l: [i for i in l if i is not None]


# Lexical Tokens
question_prefix = string("Q:").map(QuestionPrefix)
answer_prefix = string("A:").map(AnswerPrefix)
lbrace = string("{").map(LeftBrace)
rbrace = string("}").map(RightBrace)

not_text = question_prefix | answer_prefix | lbrace | rbrace | eol

# TODO: Should we define (<any_char>\n?)+ as text instead?
# abc\nabc = text
# abc\n = text
# abc\n\n = text + eol
text = (not_text.should_fail("text") >> any_char).at_least(1).concat().map(Text)
statement = not_text | text

lexer = statement.many()
