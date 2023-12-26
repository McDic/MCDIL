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
    clear_global_cls,
    emplace_global_cl,
    pop_global_cl,
)
from .parser import parse
from .reader import read

T_P = typing.ParamSpec("T_P")
T_R = typing.TypeVar("T_R")
T_NODE = typing.TypeVar("T_NODE", ParseTree, Token, ParseTree | Token)
T_COMPONENT = typing.TypeVar("T_COMPONENT", bound=AbstractComponent)

SEMANTIC_IMPLEMENTER = typing.Callable[
    typing.Concatenate["Compiler", T_NODE, T_COMPONENT, Path | URL, T_P],
    None,
]


def _convenient_impl_rule(*wanted_rule: str):
    """
    A decorator to make semantic implementer for rule more convenient.
    """

    for rule in wanted_rule:
        if rule != rule.lower():
            raise ValueError("Rule %s is not a lowercased letter" % (rule,))

    def real_decorator(
        func: SEMANTIC_IMPLEMENTER[ParseTree, T_COMPONENT, T_P]
    ) -> SEMANTIC_IMPLEMENTER[ParseTree | Token, T_COMPONENT, T_P]:
        """
        The real decorator returned by this function.
        """

        def inner_func(
            self: "Compiler",
            now: ParseTree | Token,
            current_component: T_COMPONENT,
            this_path: Path | URL,
            *args: T_P.args,
            **kwargs: T_P.kwargs,
        ) -> None:
            """
            Inner body function transformed by this decorator.
            """
            added_cl = emplace_global_cl(now, this_path)
            if isinstance(now, Token):
                raise errors.WrongComponentMeta("Unexpected token %s" % (now,))
            elif now.data not in wanted_rule:
                raise errors.UnexpectedParseTree(now)
            func(self, now, current_component, this_path, *args, **kwargs)
            if added_cl:
                pop_global_cl()

        return inner_func

    return real_decorator


def _convenient_impl_terminal(*wanted_token_type: str):
    """
    A decorator to make semantic implementer for terminal more convenient.
    """

    for token_type in wanted_token_type:
        if token_type != token_type.upper():
            raise ValueError("Token type %s is not a uppercased letter" % (token_type,))

    def real_decorator(
        func: SEMANTIC_IMPLEMENTER[Token, T_COMPONENT, T_P]
    ) -> SEMANTIC_IMPLEMENTER[ParseTree | Token, T_COMPONENT, T_P]:
        """
        The real decorator returned by this function.
        """

        def inner_func(
            self: "Compiler",
            now: ParseTree | Token,
            current_component: T_COMPONENT,
            this_path: Path | URL,
            *args: T_P.args,
            **kwargs: T_P.kwargs,
        ) -> None:
            """
            Inner body function transformed by this decorator.
            """
            added_cl = emplace_global_cl(now, this_path)
            if not isinstance(now, Token):
                raise errors.WrongComponentMeta("Unexpected rule %s" % (now.data,))
            elif now.type not in wanted_token_type:
                raise errors.UnexpectedParseTree(now)
            func(self, now, current_component, this_path, *args, **kwargs)
            if added_cl:
                pop_global_cl()

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

    def set_code_cache(self, base_path: Path | URL, source_code: str) -> None:
        """
        Try to set the code cache.
        """
        if base_path in self._code_cache:
            if source_code != self._code_cache[base_path]:
                raise errors.MCDILError(
                    "Different code cached on base_path = %s" % (base_path,)
                )
        else:
            self._code_cache[base_path] = source_code

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
            clear_global_cls()

        if source is None:  # No source is given; Read and parse
            source_code, base_path = read(str(source_path), code_cache=self._code_cache)
            now = parse(source_code)
            self.set_code_cache(base_path, source_code)
        elif isinstance(source, str):  # Source is code string; Parse only
            now = parse(source)
            base_path = source_path
            self.set_code_cache(base_path, source)
        else:  # Source is a parsed node; Just propagate directly
            now = source
            base_path = source_path

        # Implement whole program semantics
        result = NamespaceDefinition(identifier=ROOT_NAMESPACE_NAME)
        self._impl_namespace_inner(now, result, base_path)

        if datapack_path is not None:
            raise NotImplementedError
        return result

    @_convenient_impl_terminal("ANY_COMMENT")
    def _impl_description(
        self, now: Token, current_component: AbstractDefinition, _: Path | URL
    ) -> None:
        """
        Implement a description on given definition component,
        which is similar to docstring in Python.
        Currently the description feature is only supported for compound statements.
        """
        content: str = now[2:].strip() if now.startswith("//") else now[2:-2].strip()
        current_component.set_description(content)

    @_convenient_impl_terminal("IDENTIFIER")
    def _raise_if_not_identifier(
        self, now: Token, _1: AbstractDefinition, _2: Path | URL
    ) -> None:
        """
        Raise if given token `now` is not an identifier.
        Nothing is implemented here because the validation is done in decorator.
        """
        pass

    @_convenient_impl_rule("namespace")
    def _impl_namespace_outer(
        self,
        now: ParseTree,
        current_component: AbstractComponent,
        this_path: Path | URL,
    ) -> None:
        """
        Construct a namespace definition and add it to current component.
        """
        offset: int = 0
        exported: bool = False
        if now.children[offset] == "export":
            offset += 1
            exported = True
        exported

        component_identifier = now.children[offset]
        self._raise_if_not_identifier(
            component_identifier, current_component, this_path
        )
        offset += 1

    @_convenient_impl_rule("namespace", "program")
    def _impl_namespace_inner(
        self,
        now: ParseTree,
        current_component: NamespaceDefinition,
        this_path: Path | URL,
    ) -> None:
        """
        Implement a namespace definition semantic.
        This is also used to implement whole program semantic.
        Suppose we are looking `general_block` or another imported code
        by `importing`, not looking at whole `namespace` definition,
        which is handled by `_impl_namespace_outer`.
        """

        for child_index, child in enumerate(now.children):
            if isinstance(child, Token):
                match child.type:
                    case "ANY_COMMENT":  # Comments are simply ignored
                        if child_index == 0:  # Docstring
                            self._impl_description(child, current_component, this_path)
                    case _:
                        raise errors.UnexpectedParseTree(child)
            else:
                match child.data:
                    case "namespace":  # Another namespace found
                        self._impl_namespace_outer(child, current_component, this_path)
