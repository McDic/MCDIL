from pathlib import Path

from lark import Visitor

from .components.base import AbstractComponent
from .components.namespace import ROOT_NAMESPACE_NAME, NamespaceDefinition
from .parser import parse


class Compiler(Visitor):
    """
    Main compiler class.
    """

    def __init__(self) -> None:
        self._current_component: AbstractComponent = NamespaceDefinition(
            identifier=ROOT_NAMESPACE_NAME
        )

    def compile(self, path: Path):
        pass


def compile(root_path: Path) -> NamespaceDefinition:
    """
    Main entry of compilation.
    """
    raise NotImplementedError
