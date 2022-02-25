from smart_bear.markdown.lexer import (
    lexer,
)
from smart_bear.markdown.parser import (
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

from pprint import pprint


def test_text():
    tokens = lexer.parse("text")
    print(tokens)
    print(text.parse(tokens))
    assert text.parse(tokens) == Text("text")


def test_text_multiple():
    tokens = lexer.parse("text\n")
    pprint(tokens)
    assert text.at_least(1).parse(tokens) == [Text("text"), Break("\n")]


def test_content():
    tokens = lexer.parse("content\ncontent")
    pprint(tokens)
    pprint(content.parse(tokens))
    assert content.parse(tokens) == Content(
        [
            Text("content"),
            Break("\n"),
            Text("content"),
        ]
    )


def test_question():
    given = "Q: Question\nExtended"
    tokens = lexer.parse(given)
    pprint(tokens)
    expected = Question(
        Content(
            [
                Text(" Question"),
                Break("\n"),
                Text("Extended"),
            ]
        )
    )
    pprint(expected)
    pprint(question.parse(tokens))
    assert question.parse(tokens) == expected


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
#     given = "Q: Question\nExtended\nA: Answer\nExtended"
#     expected = BasicPrompt(
#         question=Question(
#             Content(
#                 Text(" Question"),
#                 Break("\n"),
#                 Text("Extended"),
#             ),
#         ),
#         answer=Answer(
#             Content(
#                 Text(" Answer"),
#                 Break("\n"),
#                 Text("Extended"),
#             ),
#         ),
#     )
#     assert basic_prompt.parse(given) == expected


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
