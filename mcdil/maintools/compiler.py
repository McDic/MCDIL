import typing
from pathlib import Path

from lark import ParseTree, Token
from yarl import URL

from .. import errors
from ..components.base import AbstractComponent, AbstractDefinition
from ..components.namespace import NamespaceDefinition
from ..constants import CODE_CACHE_TYPE, ROOT_NAMESPACE_NAME
from ..context import (
    CompilationLocation,
    add_global_compilation_location,
    clear_global_compilation_location,
    pop_global_compilation_location,
)
from .parser import parse
from .reader import read

T_P = typing.ParamSpec("T_P")
T_R = typing.TypeVar("T_R")
T_NODE = typing.TypeVar("T_NODE", ParseTree, Token)
T_COMPONENT = typing.TypeVar("T_COMPONENT", bound=AbstractComponent)

SEMANTIC_IMPLEMENTER = typing.Callable[
    typing.Concatenate["Compiler", T_NODE, T_COMPONENT, Path | URL, T_P], None
]


def _convenient_impl_rule(*wanted_meta: str):
    """
    A decorator to make semantic implementer for rule more convenient.
    """

    def real_decorator(
        func: SEMANTIC_IMPLEMENTER[ParseTree, T_COMPONENT, T_P]
    ) -> SEMANTIC_IMPLEMENTER[ParseTree, T_COMPONENT, T_P]:
        """
        The real decorator returned by this function.
        """

        def inner_func(
            self: "Compiler",
            now: ParseTree,
            current_component: T_COMPONENT,
            this_path: Path | URL,
            *args: T_P.args,
            **kwargs: T_P.kwargs,
        ) -> None:
            """
            Inner body function transformed by this decorator.
            """
            if not now.meta.empty:
                compilation_location = CompilationLocation(
                    this_path, now.meta.line, now.meta.column
                )
                add_global_compilation_location(compilation_location)
            if now.data not in wanted_meta:
                raise errors.UnexpectedParseTree(now)
            func(self, now, current_component, this_path, *args, **kwargs)
            if not now.meta.empty:
                pop_global_compilation_location()

        return inner_func

    return real_decorator


def _convenient_impl_terminal(*wanted_token_type: str):
    """
    A decorator to make semantic implementer for terminal more convenient.
    """

    def real_decorator(
        func: SEMANTIC_IMPLEMENTER[Token, T_COMPONENT, T_P]
    ) -> SEMANTIC_IMPLEMENTER[Token, T_COMPONENT, T_P]:
        """
        The real decorator returned by this function.
        """

        def inner_func(
            self: "Compiler",
            now: Token,
            current_component: T_COMPONENT,
            this_path: Path | URL,
            *args: T_P.args,
            **kwargs: T_P.kwargs,
        ) -> None:
            """
            Inner body function transformed by this decorator.
            """
            if stacking := (now.line is not None and now.column is not None):
                compilation_location = CompilationLocation(
                    this_path, now.line, now.column
                )
                add_global_compilation_location(compilation_location)
            if now.type not in wanted_token_type:
                raise errors.UnexpectedParseTree(now)
            func(self, now, current_component, this_path, *args, **kwargs)
            if stacking:
                pop_global_compilation_location()

        return inner_func

    return real_decorator


class Compiler:
    """
    Main compiler class. This does all the compilation processes.
    Do not read or parse before the compiler initializes,
    put the path to the code as a parameter instead.

    Every method for semantic implementation will have following function signature:
    ```
    @care_compilation_location
    def _impl_blabla(
        self,
        now: ParseTree,
        current_component: T_COMPONENT,
        this_path: Path | URL,
    ) -> None
    ```
    """

    def __init__(self, code_cache: CODE_CACHE_TYPE | None = None) -> None:
        self._code_cache: CODE_CACHE_TYPE = code_cache or {}

    def clear_code_cache(self) -> None:
        """
        Clear all code cache.
        """
        self._code_cache.clear()

    def compile(
        self,
        source_path: Path | URL,
        source: str | ParseTree | None = None,
        datapack_path: Path | None = None,
        clear_compilation_locations: bool = True,
    ) -> NamespaceDefinition:
        """
        Main entry of whole compilation process.
        Also generate the datapack at `datapack_path`, if available.
        You must provide `source_path` to make `import` statements work correctly.
        If `source` is not given, then compiler will try
        to read and parse the code from `source_path` automatically.
        """
        if clear_compilation_locations:
            clear_global_compilation_location()

        if source is None:  # No source is given; Read and parse
            source_code, base_path = read(str(source_path), code_cache=self._code_cache)
            now = parse(source_code)
        elif isinstance(source, str):  # Source is code string; Parse only
            now = parse(source)
            base_path = source_path
        else:  # Source is a parsed node; Just propagate directly
            now = source
            base_path = source_path

        # Implement whole program semantics
        result = NamespaceDefinition(identifier=ROOT_NAMESPACE_NAME)
        self._impl_namespace(now, result, base_path)

        if datapack_path is not None:
            raise NotImplementedError
        return result

    @_convenient_impl_terminal("ANY_COMMENT")
    def _impl_description(
        self, now: Token, current_component: AbstractDefinition, this_path: Path | URL
    ) -> None:
        """
        Implement a description on given definition component,
        which is similar to docstring in Python.
        """
        content: str = now[2:].strip() if now.startswith("//") else now[2:-2].strip()
        current_component.set_description(content)

    @_convenient_impl_rule("namespace", "program")
    def _impl_namespace(
        self,
        now: ParseTree,
        current_component: NamespaceDefinition,
        this_path: Path | URL,
    ):
        """
        Implement a namespace definition semantic.
        This is also used to implement whole program semantic.
        Suppose we are looking `general_block` or another imported code
        by `importing`, not looking at whole `namespace` definition.
        """

        for i, child in enumerate(now.children):
            if isinstance(child, Token):
                match child.type:
                    case "ANY_COMMENT":  # Comments are simply ignored
                        if i == 0:  # Docstring
                            self._impl_description(child, current_component, this_path)
                    case _:
                        raise errors.UnexpectedParseTree(child)
            else:
                match child.data:
                    case "namespace":
                        pass
