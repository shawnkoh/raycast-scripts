import parsy
from parsy import whitespace, eof, any_char, regex, string

eol = string("\n")
paragraph_separator = eol.at_least(2) | (whitespace >> eof) | eof
non_whitespace = regex(r"\S")
paragraph_body = (
    non_whitespace
    + (paragraph_separator.should_fail("paragraph_separator") >> any_char)
    .many()
    .concat()
)
paragraph = whitespace.optional() >> paragraph_body << paragraph_separator


def test_paragraph():
    expected = "I am a paragraph"
    given = "I am a paragraph\n"
    assert paragraph.parse(given) == expected
    assert paragraph.parse(expected) == expected


paragraphs = paragraph.many() << whitespace.optional()


def test_paragraphs():
    expected = ["Paragraph 1", "Paragraph 2"]
    given = """
    Paragraph 1

    Paragraph 2
    """
    assert paragraphs.parse(given) == expected
    given = """

    Paragraph 1

    Paragraph 2
    """
    assert paragraphs.parse(given) == expected

    expected = ["Paragraph 1\nHere", "Paragraph 2"]
    given = "\n\n \nParagraph 1\nHere\n\nParagraph 2\n\n\n"
    assert paragraphs.parse(given) == expected


answer_prefix = string("A:")
answer = answer_prefix >> paragraph


def test_answer():
    expected = "I am an answer!\nWith Other!"
    given = "A:\n\n\nI am an answer!\nWith Other!"
    assert answer.parse(given) == expected


question_prefix = string("Q:")
question_separator = paragraph_separator | whitespace.optional() >> question_prefix
question_body = (
    non_whitespace
    + (question_separator.should_fail("question_separator") >> any_char).many().concat()
)
question = (
    question_prefix >> whitespace.optional() >> question_body << question_separator
)
# Maybe we should think in terms of defining paragraph as question | answer | paragraph rather than trying to reuse paragraph


def test_question():
    expected = "I am a question!\nWith Other!"
    given = "Q:\nI am a question!\nWith Other!"
    assert question.parse(given) == expected


basic_prompt = ((question << whitespace.optional()) + answer) | question


# def test_basic_prompt():
#     expected = ["I am a question", "I am an answer"]
#     given = """Q: I am a question
#     A: I am an answer"""
#     print("partial")
#     # this is throwing because its not even able to find another answer
#     # since the question consumed it
#     # can we use backtracking to deal with this? instead of changing question_separator?
#     print(basic_prompt.parse_partial(given))
#     assert(basic_prompt.parse(given) == expected)


lbrace = string("{") << whitespace.optional()
rbrace = whitespace.optional() >> string("}")
cloze_body = ((lbrace | rbrace).should_fail("braces") >> any_char).many().concat()
cloze = lbrace >> cloze_body << rbrace


def test_cloze():
    expected = "spaced out"
    given = "{  spaced out }"
    assert cloze.parse(given) == expected
    expected = ["para", "cloze", "gaps"]
    given = """

    I am a {para}graph with
    {cloze}s and {gaps}


    """


cloze_prompt = (cloze | any_char.result(None)).many()


def test_cloze_prompt():
    given = "I am a {sentence} with {cloze}s that may be { spaced out}"
    expected = ["sentence", "cloze", "spaced out"]
    assert list(filter(None, cloze_prompt.parse(given))) == expected
