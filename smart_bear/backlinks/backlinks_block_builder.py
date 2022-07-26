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

    return BacklinksBlock(seq(edges).map(map_edge).flatten().to_list())
