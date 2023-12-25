"""
This module provides some stuffs regarding compilation context.
This module should not import any other MCDIL modules.
"""

from dataclasses import dataclass
from pathlib import Path

from yarl import URL


@dataclass(slots=True, frozen=True)
class CompilationLocation:
    """
    Represents current context's location.
    """

    source: Path | URL
    line: int
    column: int


_global_compilation_location_stack: list[CompilationLocation] = []


def add_global_compilation_location(
    location: CompilationLocation,
) -> CompilationLocation:
    """
    Add new global compilation location on the stack.
    """
    global _global_compilation_location_stack
    _global_compilation_location_stack.append(location)
    return location


def get_global_compilation_location() -> CompilationLocation | None:
    """
    Get global context from the stack if that exists. No popping here.
    """
    return (
        _global_compilation_location_stack[-1]
        if _global_compilation_location_stack
        else None
    )


def pop_global_compilation_location() -> CompilationLocation | None:
    """
    Try to get global context and pop that from stack if exists.
    """
    return (
        _global_compilation_location_stack.pop()
        if _global_compilation_location_stack
        else None
    )


def clear_global_compilation_location() -> None:
    """
    Reset the global context.
    """
    while pop_global_compilation_location() is not None:
        pass
