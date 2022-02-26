from smart_bear.markdown.lexer import (
    lexer,
)
from smart_bear.markdown.parser import (
    basic_prompt,
    cloze_prompt,
    ClozePrompt,
    cloze,
    Cloze,
    question,
    Question,
    Text,
    BasicPrompt,
    Answer,
    answer,
    Content,
    Break,
    text,
    content,
)
from smart_bear.intelligence.test_utilities import assert_that

from pprint import pprint


def test_text():
    tokens = lexer.parse("text")
    assert_that(
        text.parse(tokens),
        Text("text"),
    )


def test_content():
    tokens = lexer.parse("content\ncontent")
    assert content.parse(tokens) == [
        Text("content"),
        Break(),
        Text("content"),
    ]


def test_question():
    tokens = lexer.parse("Q: Question\nExtended")
    expected = Question(
        [
            Text(" Question"),
            Break(),
            Text("Extended"),
        ]
    )
    assert_that(
        question.parse(tokens),
        expected,
    )


def test_question_answer():
    tokens = lexer.parse("Q: Question\nExtended\nA: Answer")
    expected = Question(
        [
            Text(" Question"),
            Break(),
            Text("Extended"),
            Break(),
        ]
    )
    assert_that(
        question.parse_partial(tokens)[0],
        expected,
    )


def test_answer():
    tokens = lexer.parse("A: Answer\nExtended")
    expected = Answer(
        [
            Text(" Answer"),
            Break(),
            Text("Extended"),
        ]
    )
    assert_that(
        answer.parse(tokens),
        expected,
    )


def test_basic_prompt():
    given = lexer.parse("Q: Question\nExtended\nA: Answer\nExtended")
    expected = BasicPrompt(
        question=Question(
            [
                Text(" Question"),
                Break(),
                Text("Extended"),
                Break(),
            ]
        ),
        answer=Answer(
            [
                Text(" Answer"),
                Break(),
                Text("Extended"),
            ]
        ),
    )
    assert_that(
        basic_prompt.parse(given),
        expected,
    )


def test_basic_prompt_question_only():
    given = lexer.parse("Q: Question\nExtended")
    expected = BasicPrompt(
        question=Question(
            [
                Text(" Question"),
                Break(),
                Text("Extended"),
            ]
        ),
        answer=None,
    )
    assert_that(
        basic_prompt.parse(given),
        expected,
    )


def test_cloze():
    given = lexer.parse("{abc}")
    expected = Cloze(
        [
            Text("abc"),
        ]
    )
    assert_that(
        cloze.parse(given),
        expected,
    )


def test_cloze_space():
    given = lexer.parse("{ abc }")
    expected = Cloze(
        [
            Text(" abc "),
        ]
    )
    assert_that(
        cloze.parse(given),
        expected,
    )


def test_cloze_lspace():
    given = lexer.parse("{ abc}")
    expected = Cloze(
        [
            Text(" abc"),
        ]
    )
    assert_that(cloze.parse(given), expected)


def test_cloze_rspace():
    given = lexer.parse("{abc }")
    expected = Cloze(
        [
            Text("abc "),
        ]
    )
    assert_that(cloze.parse(given), expected)


def test_cloze_prompt():
    given = lexer.parse("Some text {with clozes}")
    expected = ClozePrompt(
        [
            Text("Some text "),
            Cloze(
                [
                    Text("with clozes"),
                ]
            ),
        ]
    )
    assert_that(cloze_prompt.parse(given), expected)
