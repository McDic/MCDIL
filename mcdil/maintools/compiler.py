from pathlib import Path

import lark
from yarl import URL

from .. import errors
from ..components.base import AbstractComponent
from ..components.namespace import NamespaceDefinition
from ..constants import ROOT_NAMESPACE_NAME
from ..context import CompilationContext, set_global_context
from .parser import parse
from .reader import read


def compile(
    root: lark.ParseTree,
    this_path: Path | URL,
    code_cache: dict[Path | URL, lark.ParseTree] | None = None,
    root_namespace_name: str = ROOT_NAMESPACE_NAME,
) -> NamespaceDefinition:
    """
    Main entry of compilation process.
    The compilation starts from given `root_node` and `this_path`.
    This function is recursive to compile recursively imported sources.
    When you manually call this, just passing `root_node` as parameter is enough.
    """

    code_cache = code_cache or {}

    if root != "program":
        raise errors.MCDILError("The root node is not a program")

    result: NamespaceDefinition = NamespaceDefinition(identifier=root_namespace_name)

    def raise_if_unexpected_component(
        token: lark.Token | str,
        current_component: AbstractComponent,
        desired_component_type: type[AbstractComponent],
    ):
        """
        Raise if the current component is an unexpected type with current token.
        """
        if not isinstance(current_component, desired_component_type):
            raise errors.WrongComponentMeta(
                'Unexpected token "%s" on current component type "%s"'
                % (token, desired_component_type.__name__)
            )

    def construct_semantic(now: lark.ParseTree, current_component: AbstractComponent):
        """
        Perform semantic building from `now` and `current_component`.
        This function is recursive, basically transforming
        the token DAG to the semantic DAG.
        """
        if not now.meta.empty:
            set_global_context(
                CompilationContext(this_path, now.meta.line, now.meta.column)
            )

        match now.data:
            case "program" | "namespace":
                raise_if_unexpected_component(
                    now.data, current_component, NamespaceDefinition
                )
                for child in now.children:
                    pass

    construct_semantic(root, result)
    return result
