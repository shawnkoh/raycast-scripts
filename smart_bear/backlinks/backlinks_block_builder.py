from typing import Optional
from functional import seq
from .parser import (
    Backlink,
    BacklinksBlock,
    EOL,
    InlineText,
    checkinstance,
)
from .edge_builder import Edge
import parsy


def build(edges: list[Edge]) -> Optional[BacklinksBlock]:
    edges_by_from = seq(edges).group_by(lambda edge: edge.from_node.value).to_dict()
    result = []

    for from_node, edges in edges_by_from.items():
        result += [
            InlineText("* "),
            Backlink(from_node),
            EOL(),
        ]
        for edge in edges:
            result += [
                InlineText("\t* "),
                *(dedup_star | parsy.any_char).many().parse(edge.children),
                # EOL(),
            ]

    if len(result) == 0:
        return None

    return BacklinksBlock(result)


@parsy.generate
def dedup_star():
    text: InlineText = yield checkinstance(InlineText)
    if text.value[:2] == "* ":
        return InlineText(text.value[2:])
    else:
        return text
