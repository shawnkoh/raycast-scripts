from typing import List, Optional

import functional
import parsy
from attrs import define
from more_itertools import collapse
from parsy import eof, fail, seq, success

from smart_bear.markdown.lexer import (
    AnswerPrefix,
    BacklinkBlockPrefix,
    BearID,
    Break,
    CodeFence,
    Divider,
    Hashtag,
    HeadingPrefix,
    LeftBrace,
    LeftBracket,
    LeftHTMLComment,
    QuestionPrefix,
    RightBrace,
    RightBracket,
    RightHTMLComment,
    Space,
    Tag,
    Text,
    flatten_list,
    space,
)


@define
class Spacer:
    children: List[Break | Space]

    def stringify(self) -> str:
        return (
            functional.seq(self.children)
            .map(lambda x: x.stringify())
            .reduce(lambda x, y: x + y)
        )


@define
class Backlink:
    value: Text

    def stringify(self) -> str:
        return f"[[{self.value.stringify()}]]"


Inline = Tag | Backlink | Text

Content = Break | Inline


@define
class Title:
    # FIXME: This must be trimmed to disallow space at end. Unsure about start
    value: Text

    def stringify(self):
        return self.value.stringify()


@define
class FencedCodeBlock:
    info_string: Optional[Text]
    children: List[Text | Break]

    def stringify(self) -> str:
        return (self.info_string.stringify() if self.info_string else "") + (
            functional.seq(self.children)
            .map(lambda x: x.stringify())
            .reduce(lambda x, y: x + y)
        )


@define
class Question:
    children: List[Content]

    def stringify(self) -> str:
        return (
            functional.seq(self.children)
            .map(lambda x: x.stringify())
            .reduce(lambda x, y: x + y)
        )


@define
class Answer:
    children: List[Content | FencedCodeBlock]

    def stringify(self) -> str:
        return (
            functional.seq(self.children)
            .map(lambda x: x.stringify())
            .reduce(lambda x, y: x + y)
        )


@define
class BasicPrompt:
    question: Question
    answer: Optional[Answer]


@define
class Cloze:
    children: List[Content]

    def stringify(self) -> str:
        value = (
            functional.seq(self.children)
            .map(lambda x: x.stringify())
            .reduce(lambda x, y: x + y)
        )
        return f"{{{{{value}}}}}"


@define
class ClozePrompt:
    children: List[Cloze | Content]

    def stringify(self) -> str:
        count = 0

        def anki_cloze(content: Cloze | Content) -> str:
            nonlocal count
            match content:
                case Cloze():
                    value = (
                        functional.seq(content.children)
                        .map(lambda x: x.stringify())
                        .reduce(lambda x, y: x + y)
                    )
                    count += 1
                    return f"{{{{c{count}::{value}}}}}"
                case _:
                    return content.stringify()

        return functional.seq(self.children).map(anki_cloze).reduce(lambda x, y: x + y)


@define
class Paragraph:
    children: List[Content]


@define
class BacklinkBlock:
    value: Optional[Paragraph]


@define
class Heading:
    prefix: HeadingPrefix
    children: List[Inline]


Block = (
    BearID
    | Divider
    | BasicPrompt
    | ClozePrompt
    | FencedCodeBlock
    | Heading
    | BacklinkBlock
    | Paragraph
    | Spacer
)


@define
class Root:
    title: Optional[Title]
    children: List[Block]


# A question can be part of a Paragraph
# but a Paragraph cannot be part of a question


def checkinstance(Class):
    return parsy.test_item(lambda x: isinstance(x, Class), Class.__name__)


def _concatenate_texts(_list: list) -> list:
    result = []
    accumulator = None
    for element in _list:
        if isinstance(element, str):
            if accumulator is None:
                accumulator = element
            else:
                accumulator += element
        else:
            if accumulator is not None:
                result.append(Text(accumulator))
                accumulator = None
            result.append(element)
    if accumulator is not None:
        result.append(Text(accumulator))
    return result


text = checkinstance(Text)
eol = checkinstance(Break)
answer_prefix = checkinstance(AnswerPrefix)
question_prefix = checkinstance(QuestionPrefix)
lbrace = checkinstance(LeftBrace)
rbrace = checkinstance(RightBrace)
lbracket = checkinstance(LeftBracket)
rbracket = checkinstance(RightBracket)
divider = checkinstance(Divider)
hashtag = checkinstance(Hashtag)
tag = checkinstance(Tag)
code_fence = checkinstance(CodeFence)

leftHTMLComment = checkinstance(LeftHTMLComment)
rightHTMLComment = checkinstance(RightHTMLComment)
heading_prefix = checkinstance(HeadingPrefix)

bear_id = checkinstance(BearID)

_raw_text = (
    text.map(lambda x: x.value)
    | hashtag.map(lambda _: "#")
    | lbracket.map(lambda _: "[")
    | rbracket.map(lambda _: "]")
    | lbrace.map(lambda _: "{")
    | rbrace.map(lambda _: "}")
    | question_prefix.map(lambda _: "Q:")
    | answer_prefix.map(lambda _: "A:")
    | heading_prefix.map(lambda x: x.stringify())
    | tag.map(lambda x: "#" + x.value)
    | code_fence.map(lambda _: "```")
    | leftHTMLComment.map(lambda _: "<!--")
    | rightHTMLComment.map(lambda _: "<!--")
)

_converted_brackets = (
    (rbracket.times(2).should_fail("no 2 rbracket") >> _raw_text).at_least(1).concat()
).map(Text)
backlink = lbracket.times(2) >> _converted_brackets.map(Backlink) << rbracket.times(2)

_inline = backlink | tag | _raw_text
_content = eol | _inline
# FIXME: This might be problematic because _raw_text can consume the others.
contents = _content.at_least(1).map(_concatenate_texts)

question = question_prefix >> (
    (
        (eol.times(2) | eol >> question_prefix | eol >> answer_prefix).should_fail(
            "question_prefix"
        )
        >> _content
    )
    .at_least(1)
    .map(_concatenate_texts)
    .map(Question)
)


fenced_code_block = seq(
    _prefix=code_fence,
    info_string=text.optional() << eol,
    children=(
        (
            (eol >> code_fence).should_fail("suffix")
            >> (eol | _raw_text.at_least(1).concat().map(Text))
        ).many()
    ),
    _suffix=eol >> code_fence,
).combine_dict(FencedCodeBlock)

answer = answer_prefix >> (
    (
        seq(eol, fenced_code_block)
        | (
            (eol.times(2) | eol >> question_prefix).should_fail("answer_prefix")
            >> _content
        )
        .at_least(1)
        .map(_concatenate_texts)
    ).map(Answer)
)

basic_prompt = seq(question=question << eol, answer=answer.optional(),).combine_dict(
    BasicPrompt
) | question.map(lambda x: BasicPrompt(question=x, answer=None))


cloze = (
    lbrace.times(2)
    >> (
        ((lbrace.times(2) | rbrace.times(2)).should_fail("no brace") >> _content)
        .at_least(1)
        .map(_concatenate_texts)
    )
    << rbrace.times(2)
).map(Cloze)

block_separator = eol.at_least(2)
paragraph_separator_should_fail = block_separator.should_fail("no separator")

cloze_prompt = (
    seq(
        (cloze | tag | backlink | _raw_text).at_least(1).map(_concatenate_texts),
        # FIXME: We might have to use the same separator as paragraph
        (eol.times(2).should_fail("no separator") >> (cloze | _content))
        .many()
        .map(_concatenate_texts),
    )
    .map(lambda x: list(collapse(x)))
    .bind(
        lambda res: success(ClozePrompt(res))
        if any(isinstance(ele, Cloze) for ele in res)
        else fail("no cloze")
    )
)


paragraph = (
    seq(
        (tag | backlink | _raw_text).at_least(1).map(_concatenate_texts),
        ((eol.times(2) | eol >> code_fence | eol >> eof).should_fail("sep") >> _content)
        .many()
        .map(_concatenate_texts),
    )
    .map(flatten_list)
    .map(Paragraph)
)


spacer = (eol | space).at_least(1).map(Spacer)

backlink_block_prefix = checkinstance(BacklinkBlockPrefix)

backlink_block = backlink_block_prefix >> eol >> paragraph.optional().map(BacklinkBlock)

heading = seq(
    prefix=heading_prefix,
    children=_inline.many().map(_concatenate_texts),
).combine_dict(Heading)

not_catch_all = (
    spacer
    | divider
    | basic_prompt
    | fenced_code_block
    | cloze_prompt
    | backlink_block
    | heading
    | bear_id
    | paragraph
)

catch_all = (
    (not_catch_all.should_fail("not_catch_all") >> (tag | backlink | _raw_text))
    .at_least(1)
    .map(_concatenate_texts)
    .map(Paragraph)
)

block = not_catch_all | catch_all


title = (
    (eol.should_fail("no eol") >> _raw_text).at_least(1).concat().map(Text).map(Title)
)

parser = seq(
    title=title.optional() << eol.optional(),
    children=block.many(),
).combine_dict(Root)
