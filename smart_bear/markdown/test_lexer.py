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
question_prefix = string("Q:").map(QuestionPrefix)
answer_prefix = string("A:").map(AnswerPrefix)
lbrace = string("{").map(LeftBrace)
rbrace = string("}").map(RightBrace)
# TODO: I think separator as defined here is a utility and not a token!
separator = (
    eol.at_least(2).concat()
    | (whitespace << question_prefix)
    | (whitespace << answer_prefix)
    | (whitespace << eof)
).map(Separator)

# TODO: Unsure if this is a lexical token?
text = (separator.should_fail("separator") >> any_char).many().concat().map(Text)


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
    assert separator.parse(given) == expected


def test_separator_answer():
    given = "\nA:"
    expected = Separator("\n")
    assert separator.parse(given) == expected


question = seq(question_prefix, text)


def test_question():
    given = "Q: I am a question"
    expected = [QuestionPrefix("Q:"), Text(" I am a question")]
    assert question.parse(given) == expected


answer = seq(answer_prefix, text)


def test_answer():
    given = "A: I am an Answer"
    expected = [AnswerPrefix("A:"), Text(" I am an Answer")]
    assert answer.parse(given) == expected


statement = question | answer | separator | text


def test_question_two():
    given = "Q: Question 1\nQ: Question 2"
    expected = [
        QuestionPrefix("Q:"),
        Text(" Question 1"),
        Separator("\n"),
        QuestionPrefix("Q:"),
        Text(" Question 2"),
    ]
    sep = peek(separator) >> whitespace.map(Separator).map(lambda a: [a])

    tester = (
        seq(question, sep.optional())
        .map(exclude_none)
        .map(flatten_list)
        .many()
        .map(flatten_list)
    )
    pprint(tester.parse(given))
    assert tester.parse(given) == expected


def test_repeat():
    symbol = string("hi")
    breakpoint = string(";")
    lexer = (
        (seq(symbol, breakpoint) | symbol.map(lambda x: [x])).many().map(flatten_list)
    )
    # lexer = seq(symbol_until_breakpoint, breakpoint.optional()).many()
    # maybe its becaus eof that! lookahead!
    # is there no backtracking in optional?
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
    # given = "hihi;"
    # expected = ["hihi", ";"]
    # assert lexer.parse(given) == expected
    given = "hihi;hihi"
    expected = ["hihi", ";", "hihi"]

    pprint(lexer.parse(given))
    assert lexer.parse(given) == expected
