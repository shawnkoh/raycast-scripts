from typing import List, Optional

from more_itertools import collapse

import parsy
from attrs import define
from parsy import fail, seq, success, string, generate

from smart_bear.markdown.lexer import (
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
)


@define
class Space:
    pass


@define
class Spacer:
    children: List[Break | Space]


@define
class Backlink:
    value: Text


Content = Break | Backlink | Text


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


Block = BasicPrompt | ClozePrompt | Paragraph | Spacer


@define
class Root:
    title: Optional[Title]
    children: List[Block]
    bearID: Optional[BearID]


# A question can be part of a Paragraph
# but a Paragraph cannot be part of a question


def checkinstance(Class):
    return parsy.test_item(lambda x: isinstance(x, Class), Class.__name__)


text = checkinstance(Text)
eol = checkinstance(Break)
answer_prefix = checkinstance(AnswerPrefix)
question_prefix = checkinstance(QuestionPrefix)
lbrace = checkinstance(LeftBrace)
rbrace = checkinstance(RightBrace)
lbracket = checkinstance(LeftBracket)
rbracket = checkinstance(RightBracket)

leftHTMLComment = checkinstance(LeftHTMLComment)
rightHTMLComment = checkinstance(RightHTMLComment)

bearID = checkinstance(BearID)

_raw_text = (
    lbracket.map(lambda _: "[")
    | rbracket.map(lambda _: "]")
    | leftHTMLComment.map(lambda _: "<!--")
    | rightHTMLComment.map(lambda _: "<!--")
    | question_prefix.map(lambda _: "Q:")
    | answer_prefix.map(lambda _: "A:")
    | lbrace.map(lambda _: "{")
    | rbrace.map(lambda _: "}")
    | text.map(lambda x: x.value)
)

_converted_brackets = (
    (rbracket.times(2).should_fail("no 2 rbracket") >> _raw_text).at_least(1).concat()
).map(Text)
backlink = lbracket.times(2) >> _converted_brackets.map(Backlink) << rbracket.times(2)

content = eol | backlink | _raw_text.at_least(1).concat().map(Text)

question = question_prefix >> (
    (answer_prefix.should_fail("no answer_prefix") >> content).at_least(1).map(Question)
)

answer = answer_prefix >> content.at_least(1).map(Answer)

basic_prompt = (
    seq(
        question=question,
        answer=answer.optional(),
    ).combine_dict(BasicPrompt)
    | question.map(lambda x: BasicPrompt(question=x, answer=None))
)

# TODO: Investigate how to support recursive
# TODO: Implement recursive logic using brackets logic
# cloze = lbrace >> content.at_least(1).map(Cloze) << rbrace


@generate
def _braced():
    return (yield lbrace >> simple.map(Cloze) << rbrace)


def flatten(t):
    return [item for sublist in t for item in sublist]


simple = seq(
    text,
    (backlink | eol | text).many(),
).map(lambda x: list(collapse(x)))

cloze = simple | _braced


paragraph_separator = eol.at_least(2)
paragraph_separator_should_fail = paragraph_separator.should_fail("no separator")

cloze_prompt = (
    cloze.at_least(1)
    .map(lambda x: list(collapse(x)))
    .bind(
        lambda res: success(ClozePrompt(res))
        if any(isinstance(ele, Cloze) for ele in res)
        else fail("no cloze")
    )
)


paragraph = (
    seq(
        (backlink | _raw_text.at_least(1).concat().map(Text)).map(lambda x: [x]),
        (paragraph_separator_should_fail >> content).many(),
    )
    .map(flatten_list)
    .map(Paragraph)
)

space = string(" ").map(Space)
spacer = (eol | space).at_least(1).map(Spacer)

block = basic_prompt | cloze_prompt | paragraph | spacer

title = text.map(Title)

parser = seq(
    title=title.optional() << eol.optional(),
    children=block.many(),
    bearID=bearID.optional(),
    _ignore=eol.many(),
).combine_dict(Root)
