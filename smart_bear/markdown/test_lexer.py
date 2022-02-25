from pprint import pprint
from attr import define
from parsy import whitespace, eof, any_char, regex, string, seq, peek
from smart_bear.markdown.lexer import (
    lbrace,
    QuestionPrefix,
    AnswerPrefix,
    LeftBrace,
    RightBrace,
    Text,
    Separator,
    lexer,
    text,
    separator,
    exclude_none,
    flatten_list,
)


def test_text():
    given = "I am a text"
    expected = Text("I am a text")
    assert (text << any_char.many()).parse(given) == expected


def test_text_discard_question():
    given = "I am a text Q: Some random question"
    expected = Text("I am a text")
    assert (text << any_char.many()).parse(given) == expected


def test_text_discard_answer():
    given = "I am a text A: Discarded answer"
    expected = Text("I am a text")
    assert (text << any_char.many()).parse(given) == expected


def test_lbrace():
    given = "{abc"
    expected = LeftBrace("{")
    assert (lbrace << any_char.many()).parse(given) == expected


def test_lbrace_space():
    given = "{ abc"
    expected = LeftBrace("{")
    assert (lbrace << any_char.many()).parse(given) == expected


def test_separator_eol():
    given = "\n\n"
    expected = Separator(given)
    assert separator.parse(given) == expected


def test_separator_question():
    given = "\nQ:"
    expected = Separator("\n")
    assert (separator << any_char.many()).parse(given) == expected


def test_separator_answer():
    given = "\nA:"
    expected = Separator("\n")
    assert (separator << any_char.many()).parse(given) == expected


def test_lexer():
    given = "Q: Question 1\nQ: Question 2\nA:Some\nLong answer\n\nUnrelated\n\n"
    expected = [
        QuestionPrefix("Q: "),
        Text("Question 1"),
        Separator("\n"),
        QuestionPrefix("Q: "),
        Text("Question 2"),
        Separator("\n"),
        AnswerPrefix("A:"),
        Text("Some\nLong answer"),
        Separator("\n\n"),
        Text("Unrelated"),
        Separator("\n\n"),
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
