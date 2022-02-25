from pprint import pprint
from attr import define
from parsy import whitespace, eof, any_char, regex, string, seq, peek


@define
class Separator:
    raw_value: str


@define
class QuestionPrefix:
    raw_value: str


@define
class AnswerPrefix:
    raw_value: str


@define
class LeftBrace:
    raw_value: str


@define
class RightBrace:
    raw_value: str


@define
class Text:
    raw_value: str


# Utilities
eol = string("\n")
flatten_list = lambda ls: sum(ls, [])
exclude_none = lambda l: [i for i in l if i is not None]


# Lexical Tokens
question_prefix = (string("Q:") + whitespace.optional().map(lambda x: x or "")).map(
    QuestionPrefix
)
answer_prefix = (string("A:") + whitespace.optional().map(lambda x: x or "")).map(
    AnswerPrefix
)
lbrace = string("{").map(LeftBrace)
rbrace = string("}").map(RightBrace)
separator_identity = (
    eol.at_least(2)
    | (whitespace << question_prefix)
    | (whitespace << answer_prefix)
    | (whitespace << eof)
)
separator = peek(separator_identity) >> whitespace.map(Separator)

# TODO: Unsure if this is a lexical token?
text = (separator.should_fail("separator") >> any_char).at_least(1).concat().map(Text)


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


statement = question_prefix | answer_prefix | separator | text
lexer = statement.many()


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
