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


# Utilities
eol = string("\n")
flatten_list = lambda ls: sum(ls, [])
exclude_none = lambda l: [i for i in l if i is not None]


# Lexical Tokens
question_prefix = (string("Q:") + whitespace.optional().map(lambda x: x or "")).map(
    QuestionPrefix
)
answer_prefix = (string("A:") + whitespace.optional().map(lambda x: x or "")).map(
    AnswerPrefix
)
lbrace = string("{").map(LeftBrace)
rbrace = string("}").map(RightBrace)
separator_identity = (
    eol.at_least(2)
    | (whitespace << question_prefix)
    | (whitespace << answer_prefix)
    | rbrace
    | lbrace
    | (whitespace << eof)
)
separator = peek(separator_identity) >> whitespace.map(Separator)

text = (
    (separator_identity.should_fail("separator") >> any_char)
    .at_least(1)
    .concat()
    .map(Text)
)
inline = lbrace | rbrace | text


statement = question_prefix | answer_prefix | separator | inline
lexer = statement.many()
