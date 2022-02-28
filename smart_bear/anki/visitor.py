from typing import Sequence
from smart_bear.markdown import parser
from smart_bear.anki import anki
from functional import seq


def basic_prompts(root: parser.Root) -> Sequence[anki.BasicPrompt]:
    def convert(prompt: parser.BasicPrompt) -> anki.BasicPrompt:
        return anki.BasicPrompt(
            question_md=prompt.question.stringify(),
            answer_md=prompt.answer.stringify() if prompt.answer else None,
        )

    return (
        seq(root.children)
        .filter(lambda x: isinstance(x, parser.BasicPrompt))
        .map(lambda x: convert(x))
    )


def cloze_prompts(root: parser.Root) -> Sequence[anki.ClozePrompt]:
    def stripped(prompt: parser.ClozePrompt) -> str:
        def stringify(x) -> str:
            match x:
                case parser.Cloze():
                    return (
                        seq(x.children)
                        .map(lambda x: x.stringify())
                        .reduce(lambda x, y: x + y)
                    )
                case _:
                    return x.stringify()
        return seq(prompt.children).map(stringify).reduce(lambda x, y: x + y)

    def clozed(prompt: parser.ClozePrompt) -> str:
        return (
            seq(prompt.children).map(lambda x: x.stringify()).reduce(lambda x, y: x + y)
        )

    def convert(prompt: parser.ClozePrompt) -> anki.ClozePrompt:
        return anki.ClozePrompt(
            stripped_md=stripped(prompt),
            clozed_md=clozed(prompt)
        )

    return (
        seq(root.children)
        .filter(lambda x: isinstance(x, parser.ClozePrompt))
        .map(lambda x: convert(x))
    )
