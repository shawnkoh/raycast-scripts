from pprint import pp, pprint

from pytest import raises
from parsy import string

from smart_bear.intelligence.test_utilities import assert_that
from smart_bear.markdown.lexer import lexer
from smart_bear.markdown.parser import (
    title,
    Title,
    Answer,
    BasicPrompt,
    Break,
    Cloze,
    ClozePrompt,
    Paragraph,
    Question,
    Text,
    answer,
    basic_prompt,
    cloze,
    cloze_prompt,
    content,
    paragraph,
    paragraphs,
    question,
    text,
    parser,
    Root,
)


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


def test_concat():
    given = ""
    expected = ""
    _parser = string("[").many().concat() + string("]").many().concat()
    pprint(_parser.parse(given))
    assert given == expected


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


def test_title():
    tokens = lexer.parse("Simple")
    expected = Title(Text("Simple"))
    assert_that(title.parse(tokens), expected)


def test_title_eol():
    tokens = lexer.parse("Simple\nSimple")
    expected = Title(Text("Simple"))
    assert_that(title.parse_partial(tokens)[0], expected)


def test_parser():
    tokens = lexer.parse(
        """# Smart Bear
Paragraph 1

Paragraph 2
"""
    )
    expected = Root(
        title=Title(Text("# Smart Bear")),
        children=[
            Paragraph(
                [
                    Text("Paragraph 1"),
                ]
            ),
            Paragraph(
                [
                    Text("Paragraph 2"),
                    Break(),
                ]
            ),
        ],
        bearID=None,
    )
    assert_that(parser.parse(tokens), expected)
