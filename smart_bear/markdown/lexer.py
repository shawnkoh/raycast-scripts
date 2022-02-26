from attrs import define
from parsy import any_char, eof, peek, string, whitespace


@define
class Separator:
    raw_value: str


@define
class QuestionPrefix:
    pass


@define
class AnswerPrefix:
    pass


@define
class LeftBrace:
    pass


@define
class RightBrace:
    pass


@define
class Text:
    raw_value: str


@define
class Break:
    pass


# Utilities
eol = string("\n").map(lambda x: Break())
flatten_list = lambda ls: sum(ls, [])
exclude_none = lambda l: [i for i in l if i is not None]


# Lexical Tokens
question_prefix = string("Q:").map(lambda x: QuestionPrefix())
answer_prefix = string("A:").map(lambda x: AnswerPrefix())
lbrace = string("{").map(lambda x: LeftBrace())
rbrace = string("}").map(lambda x: RightBrace())

not_text = question_prefix | answer_prefix | lbrace | rbrace | eol

# TODO: Should we define (<any_char>\n?)+ as text instead?
# abc\nabc = text
# abc\n = text
# abc\n\n = text + eol
text = (not_text.should_fail("text") >> any_char).at_least(1).concat().map(Text)
statement = not_text | text

lexer = statement.many()
