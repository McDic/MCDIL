from dataclasses import dataclass
from pathlib import Path

from yarl import URL


@dataclass(slots=True, frozen=True)
class CompilationContext:
    source: Path | URL
    line: int
    column: int


_global_context: CompilationContext | None = None


def set_global_context(new_context: CompilationContext) -> None:
    """
    Set new global compilation context.
    """
    global _global_context
    _global_context = new_context


def get_global_context() -> CompilationContext | None:
    """
    Try to get global context.
    """
    return _global_context


def clear_global_context() -> None:
    """
    Reset the global context.
    """
    global _global_context
    _global_context = None
