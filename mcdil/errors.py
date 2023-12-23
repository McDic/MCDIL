"""
This module provides all exceptions of MCDIL module.
"""

import typing

from .context import CompilationContext, get_global_context


class MCDILError(Exception):
    """
    General exception of MCDIL error.
    """


@typing.final
class SourceCodeFetchFailed(MCDILError):
    """
    Raised when failed to fetch the source code.
    """


class CompilationError(MCDILError):
    """
    General exception of all MCDIL compilation errors.
    """

    def __init__(
        self, message: str, *, context: CompilationContext | None = None
    ) -> None:
        self.context = context or get_global_context()
        if self.context is None:
            super().__init__("Compile error; %s" % (message,))
        else:
            super().__init__(
                "Compile error at %s:%d:%d; %s"
                % (self.context.source, self.context.line, self.context.column, message)
            )


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


class AbstractCollision(CompilationError, NameError):
    """
    Abstract base of all kind of collisions.
    """


@typing.final
class IdenfitierCollision(AbstractCollision, IdentifierError):
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
