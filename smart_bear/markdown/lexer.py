from typing import List

import functional
from attrs import define, field
from parsy import any_char, peek, string


@define
class Break:
    def stringify(self) -> str:
        return "\n"


@define
class Space:
    def stringify(self) -> str:
        return " "


@define
class Separator:
    value: List[Space] | Break

    def stringify(self) -> str:
        match self.value:
            case Break():
                return self.value.stringify()
            case _:
                return (
                    functional.seq(self.children)
                    .map(lambda x: x.stringify())
                    .reduce(lambda x, y: x + y)
                )


@define
class QuestionPrefix:
    suffix: Separator

    def stringify(self) -> str:
        return f"A:{self.suffix.stringify()}"


@define
class AnswerPrefix:
    suffix: Separator

    def stringify(self) -> str:
        return f"A:{self.suffix.stringify()}"


@define
class LeftBrace:
    def stringify(self) -> str:
        return "{"


@define
class RightBrace:
    def stringify(self) -> str:
        return "}"


@define
class LeftBracket:
    def stringify(self) -> str:
        return "["


@define
class RightBracket:
    def stringify(self) -> str:
        return "]"


@define
class Text:
    value: str = field()

    @value.validator
    def check(self, attribute, val):
        if "".__eq__(val):
            raise ValueError("No empty strings")

    def stringify(self) -> str:
        return self.value


@define
class LeftHTMLComment:
    def stringify(self) -> str:
        return "<!--"


@define
class RightHTMLComment:
    def stringify(self) -> str:
        return "-->"


@define
class Divider:
    def stringify(self) -> str:
        return "---"


@define
class Hashtag:
    def stringify(self) -> str:
        return "#"


@define
class Tag:
    value: str

    def stringify(self) -> str:
        return f"#{self.value}"


@define
class BearID:
    value: str

    def stringify(self) -> str:
        return f"<!-- {{BearID:{self.value}}} -->"


@define
class CodeFence:
    def stringify(self) -> str:
        return "```"


@define
class BacklinkBlockPrefix:
    def stringify(self) -> str:
        return "## Backlinks"


@define
class HeadingPrefix:
    # 1-6
    depth: int

    def stringify(self) -> str:
        return "#" * self.depth + " "


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
bear_id = (
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
heading_prefix = (
    peek(eol.optional()) >> hashtag.times(1, 6).map(len).map(HeadingPrefix) << space
)

tag = (
    hashtag.times(1)
    >> ((space | hashtag | eol).should_fail("no eol") >> any_char).at_least(1).concat()
).map(Tag)
code_fence = string("```").map(lambda _: CodeFence())
backlink_block_prefix = string("## Backlinks").map(lambda _: BacklinkBlockPrefix())

not_text = (
    question_prefix
    | answer_prefix
    | eol
    | lbrace
    | rbrace
    | lbracket
    | rbracket
    | divider
    | tag
    | backlink_block_prefix
    | heading_prefix
    | hashtag
    | code_fence
    | bear_id
    | leftHTMLComment
    | rightHTMLComment
)

text = (not_text.should_fail("text") >> any_char).at_least(1).concat().map(Text)
statement = not_text | text

lexer = statement.many()
