"""
This module provides all exceptions of MCDIL module.
"""

from requests import ConnectionError


class MCDILError(Exception):
    """
    General exception of MCDIL error.
    """


class SourceCodeFetchFailed(MCDILError, ConnectionError):
    """
    Raised when failed to fetch the source code.
    """


class IdentifierError(MCDILError, NameError):
    """
    Raised when there is a problem on identifier.
    """


class KeywordIdentifier(IdentifierError):
    """
    Raised when the identifier is a keyword.
    """


class IdentifierNotExists(IdentifierError):
    """
    Raised when tried to access non-existent identifier.
    """


class AbstractCollision(MCDILError, NameError):
    """
    Abstract base of all name/id collisions.
    """


class ComponentIDCollision(AbstractCollision):
    """
    Raised when different component ID of same type are duplicated.
    """


class IdenfitierCollision(AbstractCollision, IdentifierError):
    """
    Raised when different variable of same name already exists in this scope.
    """
