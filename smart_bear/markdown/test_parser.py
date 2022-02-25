import parsy
from smart_bear.markdown.lexer import QuestionPrefix, AnswerPrefix, Text

from attrs import define


@define
class Question:
    prefix: QuestionPrefix
    text: Text


class Answer:
    prefix: AnswerPrefix
    text: Text
