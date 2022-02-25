from smart_bear.markdown.parser import (
    question,
    Question,
    QuestionPrefix,
    Text,
    BasicPrompt,
    Answer,
    answer,
    AnswerPrefix,
    basic_prompt,
)

from pprint import pprint


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
    assert basic_prompt.parse(given) == expected
