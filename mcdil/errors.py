"""
This module provides all exceptions of MCDIL module.
"""


class MCDILError(Exception):
    """
    General exception of MCDIL error.
    """


class AbstractCollision(MCDILError, NameError):
    """
    Abstract base of all name/id collisions.
    """


class ComponentIDCollision(AbstractCollision):
    """
    Raised when different component ID of same type are duplicated.
    """


class IdenfitierCollision(AbstractCollision):
    """
    Raised when different variable of same name already exists in this scope.
    """
