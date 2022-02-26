from pprint import pprint
from attr import define
from parsy import whitespace, eof, any_char, regex, string, seq, peek
from smart_bear.markdown.lexer import (
    Break,
    lbrace,
    QuestionPrefix,
    AnswerPrefix,
    LeftBrace,
    RightBrace,
    Text,
    Separator,
    lexer,
    text,
    exclude_none,
    flatten_list,
)


def test_text():
    given = "I am a text"
    expected = Text("I am a text")
    assert (text << any_char.many()).parse(given) == expected


def test_text_discard_question():
    given = "I am a text Q: Some random question"
    expected = Text("I am a text ")
    assert (text << any_char.many()).parse(given) == expected


def test_text_discard_answer():
    given = "I am a text A: Discarded answer"
    expected = Text("I am a text ")
    assert (text << any_char.many()).parse(given) == expected


def test_lbrace():
    given = "{abc"
    expected = LeftBrace("{")
    assert (lbrace << any_char.many()).parse(given) == expected


def test_lbrace_space():
    given = "{ abc"
    expected = LeftBrace("{")
    assert (lbrace << any_char.many()).parse(given) == expected


def test_lexer():
    given = "Q: Question 1\nQ: Question 2\nA:Some\nLong answer\n\nUnrelated\n\n"
    expected = [
        QuestionPrefix("Q:"),
        Text(" Question 1"),
        Break(),
        QuestionPrefix("Q:"),
        Text(" Question 2"),
        Break(),
        AnswerPrefix("A:"),
        Text("Some"),
        Break(),
        Text("Long answer"),
        Break(),
        Break(),
        Text("Unrelated"),
        Break(),
        Break(),
    ]
    assert lexer.parse(given) == expected


def test_repeat():
    symbol = string("hi")
    breakpoint = string(";")
    lexer = (
        (seq(symbol, breakpoint) | symbol.map(lambda x: [x])).many().map(flatten_list)
    )
    given = "hihi;"
    expected = ["hi", "hi", ";"]
    assert lexer.parse(given) == expected
    given = "hihi;hihi"
    expected = ["hi", "hi", ";", "hi", "hi"]
    assert lexer.parse(given) == expected
    pprint(lexer.parse(given))


def test_repeat_two():
    symbol = string("hi")
    breakpoint = string(";")
    # NB: This MUST be at_least(1) and NOT many()
    symbol_until_breakpoint = (
        (breakpoint.should_fail("not ;") >> symbol).at_least(1).concat()
    )
    lexer = (
        seq(symbol_until_breakpoint, breakpoint.optional())
        .map(exclude_none)
        .many()
        .map(flatten_list)
    )
    given = "hihi;hihi"
    expected = ["hihi", ";", "hihi"]

    pprint(lexer.parse(given))
    assert lexer.parse(given) == expected
