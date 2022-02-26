from parsy import any_char
from smart_bear.markdown.lexer import (
    AnswerPrefix,
    QuestionPrefix,
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
    checkinstance,
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
    assert_that(
        content.parse(tokens),
        Content(
            [
                Text("content"),
                Break("\n"),
                Text("content"),
            ],
        ),
    )


def test_fuck():
    tokens = lexer.parse("Q: Question")
    expected = Question(
        Content(
            [
                Text(" Question"),
            ]
        )
    )
    no_answer_prefix = checkinstance(AnswerPrefix).should_fail("no answer prefix")
    _content = (no_answer_prefix >> checkinstance(Text)).at_least(1).map(Content)
    _parser = checkinstance(QuestionPrefix) >> _content.map(Question)
    assert_that(_parser.parse(tokens), expected)


def test_question():
    tokens = lexer.parse("Q: Question\nExtended")
    expected = Question(
        Content(
            [
                Text(" Question"),
                Break("\n"),
                Text("Extended"),
            ]
        )
    )
    assert_that(
        question.parse(tokens),
        expected,
    )


# def test_question_answer():
#     tokens = lexer.parse("Q: Question\nExtended\nA: Answer")
#     expected = Question(
#         Content(
#             [
#                 Text(" Question"),
#                 Break("\n"),
#                 Text("Extended"),
#                 Break("\n"),
#             ]
#         )
#     )
#     assert_that(question.parse(tokens), expected)


def test_answer():
    tokens = lexer.parse("A: Answer\nExtended")
    expected = Answer(
        Content(
            [
                Text(" Answer"),
                Break("\n"),
                Text("Extended"),
            ]
        )
    )
    assert answer.parse(tokens) == expected


# def test_basic_prompt():
#     given = lexer.parse("Q: Question\nExtended\nA: Answer\nExtended")
#     expected = BasicPrompt(
#         question=Question(
#             Content(
#                 [
#                     Text(" Question"),
#                     Break("\n"),
#                     Text("Extended"),
#                 ]
#             ),
#         ),
#         answer=Answer(
#             Content(
#                 [
#                     Text(" Answer"),
#                     Break("\n"),
#                     Text("Extended"),
#                 ]
#             ),
#         ),
#     )
#     assert_that(
#         basic_prompt.parse(given),
#         expected,
#     )


# def test_basic_prompt_question_only():
#     given = "Q: Question\nExtended"
#     expected = BasicPrompt(
#         question=Question(
#             Text(" Question\nExtended"),
#         ),
#         answer=None,
#     )
#     assert basic_prompt.parse(given) == expected


# def test_cloze():
#     given = "{abc}"
#     expected = Cloze(
#         Text("abc"),
#     )
#     assert cloze.parse(given) == expected


# def test_cloze_space():
#     given = "{ abc }"
#     expected = Cloze(
#         Text(" abc "),
#     )
#     assert cloze.parse(given) == expected


# def test_cloze_lspace():
#     given = "{ abc}"
#     expected = Cloze(
#         Text(" abc"),
#     )
#     assert cloze.parse(given) == expected


# def test_cloze_rspace():
#     given = "{abc }"
#     expected = Cloze(
#         Text("abc "),
#     )
#     assert cloze.parse(given) == expected


# def test_cloze_prompt():
#     given = "Some text {with clozes}"
#     expected = ClozePrompt(
#         children=[
#             Content(
#                 Text("Some text "),
#             ),
#             Cloze(
#                 Text("with clozes"),
#             ),
#         ]
#     )
#     assert (cloze_prompt.parse(given)) == expected
