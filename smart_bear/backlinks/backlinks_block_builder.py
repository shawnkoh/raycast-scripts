from typing import Optional
from functional import seq

from smart_bear.backlinks.lexer import ListItemPrefix
from .parser import (
    Backlink,
    BacklinksBlock,
    EOL,
    ListItem,
)
from .edge_builder import Edge
import parsy


def build(edges: list[Edge]) -> Optional[BacklinksBlock]:
    edges_by_from = seq(edges).group_by(lambda edge: edge.from_node.value).to_dict()
    result = []

    for from_node, edges in edges_by_from.items():
        result += [
            ListItem(
                prefix=ListItemPrefix("* "),
                children=[
                    Backlink(from_node),
                ],
            ),
            EOL(),
        ]
        for edge in edges:
            result += [
                ListItem(
                    prefix=ListItemPrefix("\t* "),
                    children=parsy.any_char.many().parse(edge.children),
                ),
                EOL(),
            ]

    if len(result) == 0:
        return None

    return BacklinksBlock(result)
