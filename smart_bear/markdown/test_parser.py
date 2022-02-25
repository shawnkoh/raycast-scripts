from pprint import pprint
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


def test_question():
    given = "Q: Question\nExtended"
    expected = Question(prefix=QuestionPrefix("Q: "), text=Text("Question\nExtended"))
    assert question.parse(given) == expected


def test_answer():
    given = "A: Answer\nExtended"
    expected = Answer(prefix=AnswerPrefix("A: "), text=Text("Answer\nExtended"))
    assert answer.parse(given) == expected


def test_basic_prompt():
    given = "Q: Question\nExtended\nA: Answer\nExtended"
    expected = BasicPrompt(
        question=Question(
            prefix=QuestionPrefix("Q: "), text=Text("Question\nExtended")
        ),
        answer=Answer(prefix=AnswerPrefix("A: "), text=Text("Answer\nExtended")),
    )
    assert basic_prompt.parse(given) == expected


def test_basic_prompt_question_only():
    given = "Q: Question\nExtended"
    expected = BasicPrompt(
        question=Question(
            prefix=QuestionPrefix("Q: "), text=Text("Question\nExtended")
        ),
        answer=None,
    )
    pprint(basic_prompt.parse(given))
    assert basic_prompt.parse(given) == expected
