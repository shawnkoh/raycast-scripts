from pytest import raises
from smart_bear.markdown.lexer import (
    lexer,
)
from smart_bear.markdown.parser import (
    paragraph,
    Paragraph,
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
    paragraphs,
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
    assert content.parse_partial(tokens)[0] == Text("content")


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


def test_cloze_prompt_fails():
    tokens = lexer.parse("Some text")
    with raises(Exception) as _:
        cloze_prompt.parse(tokens)


def test_paragraph_simple():
    tokens = lexer.parse("Simple\n")
    expected = Paragraph(
        [
            Text("Simple"),
            Break(),
        ]
    )
    assert_that(paragraph.parse(tokens), expected)


def test_paragraph_multi():
    tokens = lexer.parse("Simple\n\nHello\n")
    expected = Paragraph(
        [
            Text("Simple"),
        ]
    )
    assert_that(paragraph.parse_partial(tokens)[0], expected)


def test_paragraphs():
    tokens = lexer.parse("Simple\n\nSimple")
    expected = [
        Paragraph(
            [
                Text("Simple"),
            ]
        ),
        Paragraph(
            [
                Text("Simple"),
            ]
        ),
    ]
    pprint(tokens)
    pprint(paragraphs.parse(tokens))
    assert paragraphs.parse(tokens) == expected


def test_paragraphs_eof():
    tokens = lexer.parse("Simple\n\nSimple\n")
    expected = [
        Paragraph(
            [
                Text("Simple"),
            ]
        ),
        Paragraph(
            [
                Text("Simple"),
                Break(),
            ]
        ),
    ]
    pprint(tokens)
    pprint(paragraphs.parse(tokens))
    assert paragraphs.parse(tokens) == expected
