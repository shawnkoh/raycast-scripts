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


def test_item(Class):
    return parsy.test_item(Class, type(Class).__name__)


text = test_item(Text)
eol = test_item(Break)
answer_prefix = test_item(AnswerPrefix)
question_prefix = test_item(QuestionPrefix)
lbrace = test_item(LeftBrace)
rbrace = test_item(RightBrace)

content = (text | eol).at_least(1).map(Content)


question = question_prefix >> content.map(Question)

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
