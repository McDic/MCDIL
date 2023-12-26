"""
This module provides all exceptions of MCDIL module.
"""

import typing
from pathlib import Path

from lark import ParseTree, Token
from yarl import URL

from .context import CompilationLocation, get_global_cl


class MCDILError(Exception):
    """
    General exception of MCDIL error.
    """


@typing.final
class SourceCodeFetchFailed(MCDILError):
    """
    Raised when failed to fetch the source code.
    """

    def __init__(self, source: Path | URL | str, meta: typing.Any = None):
        super().__init__(
            "Failed to fetch source from %s%s" % (source, f"; {meta}" if meta else "")
        )


class CompilationError(MCDILError):
    """
    General exception of all MCDIL compilation errors.
    """

    def __init__(self, message: str, *, CL: CompilationLocation | None = None) -> None:
        self._CL = CL or get_global_cl()
        super().__init__(
            "Compile error; %s" % (message,)
            if self._CL is None
            else "Compile error at %s:%d:%d; %s"
            % (self._CL.source, self._CL.line, self._CL.column, message)
        )


class GraphError(CompilationError):
    """
    Raised when there is a problem on graph resolution.
    """


class IdentifierError(CompilationError, NameError):
    """
    Raised when there is a problem on identifier.
    """


@typing.final
class KeywordIdentifier(IdentifierError):
    """
    Raised when the identifier is a keyword.
    """

    def __init__(self, keyword: str, **kwargs) -> None:
        super().__init__(
            "%s is a keyword, can't be used as identifier" % (keyword,), **kwargs
        )


@typing.final
class IdentifierNotFound(IdentifierError):
    """
    Raised when tried to access non-existent identifier.
    """

    def __init__(self, identifier: str, **kwargs) -> None:
        super().__init__("Identifier %s not found" % (identifier,), **kwargs)


@typing.final
class IdenfitierCollision(IdentifierError):
    """
    Raised when different object of same identifier
    already exists in this scope directly.
    """

    def __init__(self, identifier: str, **kwargs) -> None:
        super().__init__(
            "Identifier %s is already direct-initialized in this scope" % (identifier,),
            **kwargs,
        )


class WrongComponentMeta(CompilationError):
    """
    Raised when this kind of component meta can't be used in current context.
    """

    def __init__(self, message: str, **kwargs) -> None:
        super().__init__(message, **kwargs)


class UnexpectedParseTree(WrongComponentMeta):
    """
    Raised when the unexpected token or parse tree is encountered.
    """

    def __init__(self, node: ParseTree | Token, **kwargs) -> None:
        super().__init__(
            "Unexpected %s encountered"
            % (
                f"token {node.type}" if isinstance(node, Token) else f"node {node.data}"
            ),
            **kwargs,
        )


@typing.final
class AuthorAlreadySet(WrongComponentMeta):
    """
    Raised when the author is already set.
    """

    def __init__(self, *, name: str, email: str, **kwargs) -> None:
        super().__init__(
            "Author %s, %s is already set on this namespace" % (name, email), **kwargs
        )


@typing.final
class NotAuthorable(WrongComponentMeta):
    """
    Raised when this component can't have an author meta information.
    """

    def __init__(self, **kwargs) -> None:
        super().__init__("This component can't have an author", **kwargs)


@typing.final
class DescriptionAlreadySet(WrongComponentMeta):
    """
    Raised when this component already has an description.
    """

    def __init__(self, **kwargs) -> None:
        super().__init__("This component already have a description", **kwargs)
