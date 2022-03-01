from typing import Sequence

from functional import pseq, seq
from tqdm import tqdm

from smart_bear.anki import anki
from smart_bear.markdown import parser
from smart_bear.markdown.lexer import lexer

IGNORE_TAG = "smart-bear/ignore-prompts"


def will_ignore(root: parser.Root) -> bool:
    def is_ignore(tag) -> bool:
        return isinstance(tag, parser.Tag) and tag.value == IGNORE_TAG
    return (
        seq(root.children)
        .exists(lambda x: isinstance(x, parser.Paragraph) and seq(x.children).exists(is_ignore))
    )


def tags(root: parser.Root) -> Sequence[str]:
    return (
        seq(root.children)
        .filter(lambda x: isinstance(x, parser.Paragraph))
        .flat_map(lambda x: seq(x.children).filter(lambda x: isinstance(x, parser.Tag)))
        .map(lambda x: x.value)
    )


def basic_prompts(root: parser.Root) -> Sequence[anki.BasicPrompt]:
    _tags = tags(root)

    def convert(prompt: parser.BasicPrompt) -> anki.BasicPrompt:
        return anki.BasicPrompt(
            question_md=prompt.question.stringify(),
            answer_md=prompt.answer.stringify() if prompt.answer else None,
            tags=_tags,
        )

    return (
        seq(root.children)
        .filter(lambda x: isinstance(x, parser.BasicPrompt))
        .map(lambda x: convert(x))
    )


def cloze_prompts(root: parser.Root) -> Sequence[anki.ClozePrompt]:
    _tags = tags(root)

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
        return prompt.stringify()

    def convert(prompt: parser.ClozePrompt) -> anki.ClozePrompt:
        return anki.ClozePrompt(
            stripped_md=stripped(prompt),
            clozed_md=clozed(prompt),
            tags=_tags,
        )

    return (
        seq(root.children)
        .filter(lambda x: isinstance(x, parser.ClozePrompt))
        .map(lambda x: convert(x))
    )

def extract_prompts(urls):
    import_basic_prompts = dict()
    import_cloze_prompts = dict()

    def parse(url) -> parser.Root:
        root = None
        with open(url) as file:
            tokens = lexer.parse(file.read())
            root = parser.parse(tokens)
        return root

    def iter(root: parser.Root):
        def assign(d, x):
            d[x.id] = x

        seq(basic_prompts(root)).for_each(
            lambda x: assign(import_basic_prompts, x)
        )
        seq(cloze_prompts(root)).for_each(
            lambda x: assign(import_cloze_prompts, x)
        )

    (pseq(tqdm(urls)).map(parse).filter_not(will_ignore).for_each(iter))
    return import_basic_prompts, import_cloze_prompts
