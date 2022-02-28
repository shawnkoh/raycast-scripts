from typing import List
from attrs import define
from parsy import any_char, eof, peek, string, whitespace


@define
class Break:
    def stringify(self):
        return "\n"


@define
class Space:
    def stringify(self):
        " "


@define
class Separator:
    value: List[Space] | Break

    def stringify(self):
        match self.value:
            case Break():
                return self.value.stringify()
            case _:
                return self.value.join(lambda x: x.stringify())


@define
class QuestionPrefix:
    suffix: Separator

    def stringify(self):
        f"A:{self.suffix.stringify()}"


@define
class AnswerPrefix:
    suffix: Separator

    def stringify(self):
        f"A:{self.suffix.stringify()}"


@define
class LeftBrace:
    def stringify(self):
        "{"


@define
class RightBrace:
    def stringify(self):
        "}"


@define
class LeftBracket:
    def stringify(self):
        "["


@define
class RightBracket:
    def stringify(self):
        "]"


@define
class Text:
    value: str

    def stringify(self):
        self.value


@define
class LeftHTMLComment:
    def stringify(self):
        "<!--"


@define
class RightHTMLComment:
    def stringify(self):
        "-->"


@define
class Divider:
    def stringify(self):
        "---"


@define
class Hashtag:
    def stringify(self):
        "#"


@define
class Tag:
    value: str

    def stringify(self):
        f"#{self.value}"


@define
class BearID:
    value: str

    def stringify(self):
        f"<!-- {{BearID:{self.value}}} -->"


@define
class CodeFence:
    def stringify(self):
        "```"


@define
class BacklinkBlockPrefix:
    def stringify(self):
        "## Backlinks"


# Utilities
eol = string("\n").map(lambda x: Break())
flatten_list = lambda ls: sum(ls, [])
exclude_none = lambda l: [i for i in l if i is not None]
space = string(" ").map(lambda x: Space())
separator = (space.many() | eol).map(Separator)


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
backlink_block_prefix = string("## Backlinks").map(lambda _: BacklinkBlockPrefix())

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
    | backlink_block_prefix
    | hashtag
    | code_fence
)

text = (not_text.should_fail("text") >> any_char).at_least(1).concat().map(Text)
statement = not_text | text

lexer = statement.many()
