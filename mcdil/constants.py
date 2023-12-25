import enum
import typing
from dataclasses import dataclass
from pathlib import Path

from yarl import URL

# Default name of root namespace.
ROOT_NAMESPACE_NAME: typing.Final[str] = "__root__"

# Type of code cache.
CODE_CACHE_TYPE = dict[Path | URL, str]

# List of hard keywords that never can be a variable name.
HARD_KEYWORDS: typing.Final[frozenset[str]] = frozenset(
    {
        # Types
        "int",
        "bool",
        "float",
        "null",
        "string",
        "deque",
        "selector",
        "D3",
        "R2",
        "map",
        "auto",
        # Literals
        "true",
        "false",
        # Qualifiers
        "immutable",
        "export",
        # Special statements
        "sleep",
        "return",
        "continue",
        "break",
        "alias",
        "author",
        # MC Command related
        "raw",
        "execute",
        # Compounds
        "function",
        "while",
        "if",
        "else",
        "namespace",
        "import",
        # Custom Types and Generics
        "struct",
        "enum",
        "typename",
        "typemap",
    }
)


@enum.verify(enum.UNIQUE)
class GenericParameterType(enum.Enum):
    """
    Enumeration of generic parameter types.
    """

    TYPENAME = enum.auto()
    INT = enum.auto()
    BOOL = enum.auto()
    TYPEMAP = enum.auto()
