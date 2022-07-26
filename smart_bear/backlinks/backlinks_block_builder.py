from functional import seq
from .parser import (
    Backlink,
    BacklinksBlock,
    EOL,
    InlineText,
)
from .edge_builder import Edge


def build(edges: list[Edge]) -> BacklinksBlock:
    def map_edge(edge: Edge):
        return [
            InlineText("* "),
            Backlink(edge.from_node.value),
            EOL(),
            # TODO: i need to fix this
            # the children have to be indented as well.
            InlineText("\t* "),
            *edge.children,
            EOL(),
        ]

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
                *edge.children,
                # EOL(),
            ]

    return BacklinksBlock(result)
