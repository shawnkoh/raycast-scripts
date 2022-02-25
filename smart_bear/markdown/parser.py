from typing import Optional
from parsy import seq
from smart_bear.markdown.lexer import (
    QuestionPrefix,
    AnswerPrefix,
    separator,
    Text,
    question_prefix,
    answer_prefix,
    text,
)

from attrs import define


@define
class Question:
    prefix: QuestionPrefix
    text: Text


@define
class Answer:
    prefix: AnswerPrefix
    text: Text


@define
class BasicPrompt:
    question: Question
    answer: Optional[Answer]


question = seq(prefix=question_prefix, text=text).combine_dict(Question)
answer = seq(prefix=answer_prefix, text=text).combine_dict(Answer)

basic_prompt = (
    seq(
        question=question,
        _separator=separator,
        answer=answer.optional(),
    ).combine_dict(BasicPrompt)
    | question.map(lambda x: BasicPrompt(question=x, answer=None))
)
