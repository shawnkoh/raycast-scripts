from typing import List, Optional

import parsy
from attrs import define
from parsy import fail, seq, success

from smart_bear.markdown.lexer import (
    AnswerPrefix,
    Break,
    LeftBrace,
    QuestionPrefix,
    RightBrace,
    Text,
)

Content = Break | Text


@define
class Title:
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
    children: List[BasicPrompt | ClozePrompt | Content]


@define
class Root:
    title: Optional[Title]
    children: List[Paragraph]


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

content = eol | text

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
cloze = lbrace >> content.at_least(1).map(Cloze) << rbrace

cloze_prompt = (
    (cloze | content)
    .at_least(1)
    .bind(
        lambda res: success(ClozePrompt(res))
        if any(isinstance(ele, Cloze) for ele in res)
        else fail("no cloze")
    )
)

paragraph_separator = eol.at_least(2)

paragraph = (
    (
        paragraph_separator.should_fail("no separator")
        >> (basic_prompt | cloze_prompt | content)
    )
    .at_least(1)
    .map(Paragraph)
)

paragraphs = paragraph.sep_by(paragraph_separator)

title = text.map(Title)

parser = seq(
    title=title.optional() << eol.optional(),
    children=paragraphs,
).combine_dict(Root)
