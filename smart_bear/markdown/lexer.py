from typing import List
from attrs import define
from parsy import any_char, eof, peek, string, whitespace


@define
class Break:
    pass


@define
class Space:
    pass


Separator = List[Space] | Break


@define
class QuestionPrefix:
    suffix: Separator


@define
class AnswerPrefix:
    suffix: Separator


@define
class LeftBrace:
    pass


@define
class RightBrace:
    pass


@define
class LeftBracket:
    pass


@define
class RightBracket:
    pass


@define
class Text:
    value: str


@define
class LeftHTMLComment:
    pass


@define
class RightHTMLComment:
    pass


@define
class Divider:
    pass


@define
class Hashtag:
    pass


# i think best solution for now - keep it in lexer.
@define
class Tag:
    value: str


# <!-- {BearID:3A72570E-59E0-4094-907F-CAC602C9A6CE-13835-00000A4715F28D3D} -->
@define
class BearID:
    value: str


@define
class CodeFence:
    pass


# Utilities
eol = string("\n").map(lambda x: Break())
flatten_list = lambda ls: sum(ls, [])
exclude_none = lambda l: [i for i in l if i is not None]
space = string(" ").map(lambda x: Space())
separator = space.many() | eol


# Lexical Tokens
question_prefix = (
    peek((space | eol).many()) >> string("Q:") >> separator.map(QuestionPrefix)
)
answer_prefix = (
    peek((space | eol).many()) >> string("A:") >> separator.map(AnswerPrefix)
)
lbrace = string("{").map(lambda x: LeftBrace())
rbrace = string("}").map(lambda x: RightBrace())
lbracket = string("[").map(lambda x: LeftBracket())
rbracket = string("]").map(lambda x: RightBracket())
leftHTMLComment = string("<!--").map(lambda x: LeftHTMLComment())
rightHTMLComment = string("-->").map(lambda x: RightHTMLComment())
bearID = (
    leftHTMLComment
    >> string(" ")
    >> lbrace
    >> string("BearID:")
    >> (rbrace.should_fail("no rbrace") >> any_char).at_least(1).concat()
    << rbrace
    << string(" ")
    << rightHTMLComment
).map(BearID)
divider = string("---").map(lambda _: Divider())
hashtag = string("#").map(lambda _: Hashtag())
tag = (
    hashtag.times(1)
    >> ((space | hashtag | eol).should_fail("no eol") >> any_char).at_least(1).concat()
).map(Tag)
code_fence = string("```").map(lambda _: CodeFence())

not_text = (
    bearID
    | question_prefix
    | answer_prefix
    | lbrace
    | rbrace
    | lbracket
    | rbracket
    | eol
    | leftHTMLComment
    | rightHTMLComment
    | divider
    | tag
    | hashtag
    | code_fence
)

# TODO: Should we define (<any_char>\n?)+ as text instead?
# abc\nabc = text
# abc\n = text
# abc\n\n = text + eol
text = (not_text.should_fail("text") >> any_char).at_least(1).concat().map(Text)
statement = not_text | text

lexer = statement.many()
