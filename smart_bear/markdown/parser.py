from typing import List, Optional

from more_itertools import collapse

import parsy
from attrs import define
from parsy import fail, seq, success, string, generate, eof

from smart_bear.markdown.lexer import (
    space,
    Space,
    Divider,
    Hashtag,
    Tag,
    flatten_list,
    AnswerPrefix,
    BearID,
    Break,
    LeftBrace,
    LeftBracket,
    LeftHTMLComment,
    RightHTMLComment,
    QuestionPrefix,
    RightBrace,
    RightBracket,
    Text,
    CodeFence,
)


@define
class Spacer:
    children: List[Break | Space]


@define
class Backlink:
    value: Text


Content = Tag | Break | Backlink | Text


@define
class Title:
    # FIXME: This must be trimmed to disallow space at end. Unsure about start
    value: Text


@define
class Question:
    children: List[Content]


@define
class Answer:
    children: List[Content]


@define
class BasicPrompt:
    question: Question
    answer: Optional[Answer]


@define
class Cloze:
    children: List[Content]


@define
class ClozePrompt:
    children: List[Cloze | Content]


@define
class Paragraph:
    children: List[Content]


@define
class BacklinkBlock:
    value: Paragraph


@define
class FencedCodeBlock:
    info_string: Optional[Text]
    children: List[Text | Break]


Block = (
    BearID | Divider | BasicPrompt | ClozePrompt | BacklinkBlock | Paragraph | Spacer
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
    | tag.map(lambda x: "#" + x.value)
    | code_fence.map(lambda _: "```")
    | leftHTMLComment.map(lambda _: "<!--")
    | rightHTMLComment.map(lambda _: "<!--")
)

_converted_brackets = (
    (rbracket.times(2).should_fail("no 2 rbracket") >> _raw_text).at_least(1).concat()
).map(Text)
backlink = lbracket.times(2) >> _converted_brackets.map(Backlink) << rbracket.times(2)

_content = eol | backlink | tag | _raw_text
# FIXME: This might be problematic because _raw_text can consume the others.
contents = _content.at_least(1).map(_concatenate_texts)

question = question_prefix >> (
    (
        (eol.times(2) | question_prefix | answer_prefix).should_fail("question_prefix")
        >> _content
    )
    .at_least(1)
    .map(_concatenate_texts)
    .map(Question)
)

answer = answer_prefix >> (
    ((eol.times(2) | question_prefix).should_fail("answer_prefix") >> _content)
    .at_least(1)
    .map(_concatenate_texts)
    .map(Answer)
)

basic_prompt = (
    seq(
        question=question,
        answer=answer.optional(),
    ).combine_dict(BasicPrompt)
    | question.map(lambda x: BasicPrompt(question=x, answer=None))
)


cloze = (
    lbrace
    >> (
        ((lbrace | rbrace).should_fail("no brace") >> _content)
        .at_least(1)
        .map(_concatenate_texts)
    )
    << rbrace
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

_backlink_block_prefix = (
    hashtag.times(2)
    >> text.bind(
        lambda x: success(x.value)
        if x.value == " Backlinks"
        else fail("no backlink block prefix")
    )
    >> eol
)

backlink_block = _backlink_block_prefix >> paragraph.map(BacklinkBlock)

not_catch_all = (
    spacer
    | divider
    | basic_prompt
    | fenced_code_block
    | cloze_prompt
    | backlink_block
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
