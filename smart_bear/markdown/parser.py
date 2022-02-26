from typing import List, Optional
from parsy import seq
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


@define
class Content:
    children: List[Text | Break]


@define
class Question:
    children: Content


@define
class Answer:
    children: Content


@define
class BasicPrompt:
    question: Question
    answer: Optional[Answer]


@define
class Cloze:
    children: Content


@define
class ClozePrompt:
    children: List[Content | Cloze]


@define
class Paragraph:
    children: List[Question | Content]


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

content = (text | eol).at_least(1).map(Content)


question = question_prefix >> (
    (answer_prefix.should_fail("no answer_prefix") >> (text | eol))
    .at_least(1)
    .map(Content)
).map(Question)

answer = answer_prefix >> content.map(Answer)

basic_prompt = (
    seq(
        question=question,
        answer=answer.optional(),
    ).combine_dict(BasicPrompt)
    | question.map(lambda x: BasicPrompt(question=x, answer=None))
)

# TODO: Investigate how to support recursive
cloze = lbrace >> content.map(Cloze) << rbrace

cloze_prompt = (text | cloze).at_least(1).map(ClozePrompt)
