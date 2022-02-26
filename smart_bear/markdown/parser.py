from operator import contains
from typing import List, Optional
from parsy import seq, fail, success, generate, eof
import parsy
from smart_bear.markdown.lexer import (
    lexer,
    flatten_list,
    exclude_none,
    Break,
    LeftBrace,
    QuestionPrefix,
    AnswerPrefix,
    RightBrace,
    Text,
)

from attrs import define

Content = Break | Text


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

paragraph = (basic_prompt | cloze_prompt | content).at_least(1).map(Paragraph) << (
    eol.at_least(2) | eol.optional() << eof
)
