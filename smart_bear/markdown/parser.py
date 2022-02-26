from typing import List, Optional

import parsy
from attrs import define
from parsy import fail, seq, success

from smart_bear.markdown.lexer import (
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
    # TODO: This is problematic for paragraphs with a single { or }
    children: Question | Answer | ClozePrompt | List[Content]


@define
class Root:
    title: Optional[Title]
    children: List[Paragraph]
    bearID: Optional[BearID]


# A question can be part of a Paragraph
# but a Paragraph cannot be part of a question


def checkinstance(Class):
    return parsy.test_item(lambda x: isinstance(x, Class), type(Class).__name__)


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
    | text.map(lambda x: x.value)
    | leftHTMLComment.map(lambda _: "<!--")
    | rightHTMLComment.map(lambda _: "<!--")
)

_converted_brackets = (
    (rbracket.times(2).should_fail("no 2 rbracket") >> _raw_text).at_least(1).concat()
).map(Text)
backlink = lbracket.times(2) >> _converted_brackets.map(Backlink) << rbracket.times(2)

content = eol | backlink | text | _raw_text.at_least(1).concat().map(Text)

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
cloze = lbrace >> content.at_least(1).map(Cloze) << rbrace

paragraph_separator = eol.at_least(2)
paragraph_separator_should_fail = paragraph_separator.should_fail("no separator")

cloze_prompt = (
    (paragraph_separator_should_fail >> (cloze | content))
    .at_least(1)
    .bind(
        lambda res: success(ClozePrompt(res))
        if any(isinstance(ele, Cloze) for ele in res)
        else fail("no cloze")
    )
)

paragraph = (
    question
    | answer
    | cloze_prompt
    | (paragraph_separator_should_fail >> (content)).at_least(1)
).map(Paragraph)

paragraphs = paragraph.sep_by(paragraph_separator)

title = text.map(Title)

parser = seq(
    title=title.optional() << eol.optional(),
    children=paragraphs,
    _skip=eol.many(),
    bearID=bearID.optional(),
    _ignore=eol.many(),
).combine_dict(Root)
