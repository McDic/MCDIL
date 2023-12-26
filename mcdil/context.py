"""
This module provides some stuffs regarding compilation context.
This module should not import any other MCDIL modules.
"""

from dataclasses import dataclass
from pathlib import Path

from lark import ParseTree, Token
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


def add_global_cl(
    location: CompilationLocation,
) -> CompilationLocation:
    """
    Add new global CL on the stack.
    """
    global _global_compilation_location_stack
    _global_compilation_location_stack.append(location)
    return location


def emplace_global_cl(now: ParseTree | Token, this_path: Path | URL) -> bool:
    """
    Construct and add global compilation location if `now` has metadata.
    Return `True` if successfully added, otherwise return `False`.
    """
    if isinstance(now, Token):
        if now.line is not None and now.column is not None:
            cl = CompilationLocation(this_path, now.line, now.column)
            add_global_cl(cl)
            return True
    else:
        if not now.meta.empty:
            cl = CompilationLocation(this_path, now.meta.line, now.meta.column)
            add_global_cl(cl)
            return True
    return False


def get_global_cl() -> CompilationLocation | None:
    """
    Get global CL from the stack if that exists. No popping here.
    """
    return (
        _global_compilation_location_stack[-1]
        if _global_compilation_location_stack
        else None
    )


def pop_global_cl() -> CompilationLocation | None:
    """
    Try to get global CL and pop that from stack if exists.
    """
    return (
        _global_compilation_location_stack.pop()
        if _global_compilation_location_stack
        else None
    )


def clear_global_cls() -> None:
    """
    Reset all global CLs in the stack.
    """
    while pop_global_cl() is not None:
        pass
