import typing

from .errors import GraphError

H = typing.TypeVar("H", bound=typing.Hashable)


class CommunicationGraph(typing.Generic[H]):
    """
    Represents a DAG specialized for MCDIL.

    Each node has zero or more inner edges and an optional outer edge,
    where each inner edge represent `parent -> child` or `parent -> external link`
    and the outer edge represent `child -> parent`, which is unique for each node.

    When the toposort is happened, only inner edges are used.
    Outer edges are reserved for something like identifier resolving.
    """

    def __init__(self) -> None:
        self._inner_edges: dict[H, set[H]] = {}
        self._outer_edges: dict[H, H] = {}

    def add_edges(self, parent: H, *children: H, is_main_link: bool = False) -> None:
        """
        Add edges between parent and children.
        If there is already an main edge, raise an error.
        """
        if parent not in self._inner_edges:
            self._inner_edges[parent] = set()
        for child in children:
            if is_main_link:
                if child in self._outer_edges:
                    raise GraphError("Child %s already has its parent" % (child,))
                self._outer_edges[child] = parent
            if child in self._inner_edges[parent]:
                raise GraphError(
                    "Child %s is already dependent to parent %s" % (child, parent)
                )
            self._inner_edges[parent].add(child)
