import hypothesis
from hypothesis import strategies as st
from parsy import any_char, seq, string
from rich.pretty import pprint

from smart_bear.intelligence.test_utilities import assert_that
from smart_bear.markdown.lexer import (
    AnswerPrefix,
    BearID,
    Break,
    HeadingPrefix,
    LeftBrace,
    QuestionPrefix,
    RightBrace,
    Separator,
    Space,
    Tag,
    Text,
    bear_id,
    exclude_none,
    flatten_list,
    heading_prefix,
    lbrace,
    lexer,
    rbrace,
    tag,
    text,
)


def test_text():
    given = "I am a text"
    expected = Text("I am a text")
    assert (text << any_char.many()).parse(given) == expected


def test_text_discard_question():
    given = "I am a text Q: Some random question"
    expected = Text("I am a text ")
    assert text.parse_partial(given)[0] == expected


def test_text_discard_answer():
    given = "I am a text A: Discarded answer"
    expected = Text("I am a text ")
    assert text.parse_partial(given)[0] == expected


@hypothesis.given(st.text().map(lambda x: "{" + x))
def test_lbrace(raw):
    assert_that(lbrace.parse_partial(raw)[0], LeftBrace())


@hypothesis.given(st.text().map(lambda x: "}" + x))
def test_rbrace(raw):
    assert_that(rbrace.parse_partial(raw)[0], RightBrace())


def test_lexer():
    given = "Q: Question 1\nQ: Question 2\nA: Some\nLong answer\n\nUnrelated\n\n"
    expected = [
        QuestionPrefix(Separator([Space()])),
        Text("Question 1"),
        Break(),
        QuestionPrefix(Separator([Space()])),
        Text("Question 2"),
        Break(),
        AnswerPrefix(Separator([Space()])),
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


def test_bear_id():
    given = (
        "<!-- {BearID:1419719E-6881-497E-94E2-BB154943963C-30579-0000CA9CD9FF92FE} -->"
    )
    expected = BearID("1419719E-6881-497E-94E2-BB154943963C-30579-0000CA9CD9FF92FE")
    assert bear_id.parse(given) == expected


@hypothesis.given(
    st.text(
        st.characters(blacklist_characters="#", blacklist_categories=["Z", "Cc"]),
        min_size=1,
    )
)
def test_tag(s):
    assert tag.parse("#" + s) == Tag(s)


@hypothesis.given(
    st.integers(1, 6).map(lambda x: "#" * x + " "),
    st.text(),
)
def test_heading_prefix(tags, text):
    tag = tags + text
    assert heading_prefix.parse_partial(tag)[0] == HeadingPrefix(depth=len(tags) - 1)
