from smart_bear.markdown.parser import BasicPrompt, ClozePrompt, Root
from functional import seq
from rich.pretty import pprint


def visit(root: Root):
    (
        seq(root.children)
        .filter(lambda x: isinstance(x, BasicPrompt))
        .for_each(lambda x: pprint(x))
    )

    (
        seq(root.children)
        .filter(lambda x: isinstance(x, ClozePrompt))
        .for_each(lambda x: pprint(x))
    )
