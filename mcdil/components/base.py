import enum
import typing
from pathlib import Path

from .. import errors

# List of hard keywords that never can be a variable name.
HARD_KEYWORDS: frozenset[str] = frozenset(
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


class AbstractComponent:
    """
    Represents an any abstract code component.
    This includes all kind of statements including

    - function definitions
    - assignable statements
    - namespace block

    and more.
    """

    def __init__(
        self,
        *,
        component_name: str | None = None,
        module_path: Path | str,
        parent: typing.Self | None = None,
        author_name: str | None = None,
        author_email: str | None = None,
    ) -> None:
        # Literal or inherited properties
        self._component_name: str | None = component_name
        self._module_path: Path | str = module_path
        self._author_name: str | None = author_name or (
            parent._author_name if parent is not None else None
        )
        self._author_email: str | None = author_email or (
            parent._author_email if parent is not None else None
        )

        # Graph properties
        self._childs: list[typing.Self] = []
        self._raw_visible_identifiers_cache: set[str] = set()

        # Parent
        self._parent: typing.Self | None = parent
        if self._parent is not None:
            self._parent._register_child(self)

    @typing.final
    def _register_child(self, child: typing.Self):
        """
        Register given `child` to this component.
        You should pass `parent` when `child` is constructed,
        instead of explicitly calling this.
        """
        self._childs.append(child)
        if (child_identifier := child.represented_identifier()) is not None:
            if child_identifier in HARD_KEYWORDS:
                raise errors.KeywordIdentifier(
                    "%s can't be an identifier" % (child_identifier,)
                )
            self._raw_visible_identifiers_cache.add(child_identifier)

    def represented_identifier(self) -> str | None:
        """
        An identifier represent this component.
        If this component is something like variable definition,
        function definition, namespace block, etc, then
        this component should return a proper identifier string.
        """
        return None

    def get_commands(self) -> list[str]:
        """
        Get list of commands that implements this component.
        If this component should not generate any command,
        then return an empty list.
        """
        raise NotImplementedError


@enum.verify(enum.UNIQUE)
class GenericParameterType(enum.Enum):
    """
    Enumeration of generic parameter types.
    """

    TYPENAME = enum.auto()
    INT = enum.auto()
    BOOL = enum.auto()
    TYPEMAP = enum.auto()


# Mapping of generic identifiers and its information.
# {
#       TN: typename -> AbstractDefinition | None
#       I:  int -> int | None
#       B:  bool -> bool | None
#       TM: typemap -> dict[str, AbstractDefinition | None] | None
# }
GENERIC_PARAMETERS = dict[
    str,
    tuple[
        GenericParameterType,
        typing.Union[
            dict[str, typing.Optional["AbstractDefinition"]],
            "AbstractDefinition",
            int,
            bool,
            None,
        ],
    ],
]


class AbstractDefinition(AbstractComponent):
    """
    Represents a definition of a variable, function,
    struct, alias, enum, namespace, etc.

    If `generic` is an empty dict, then this object
    is considered as non-generic object.
    """

    def __init__(
        self,
        *,
        identifier: str,
        # IDENTIFIER: TYPENAME/INT/BOOL/TYPEMAP
        generic: GENERIC_PARAMETERS | None = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self._identifier: typing.Final[str] = identifier
        self._generic: GENERIC_PARAMETERS = self._verify_generic_parameters(generic)

    @staticmethod
    def _verify_generic_parameters(
        generic: GENERIC_PARAMETERS | None,
    ) -> GENERIC_PARAMETERS:
        """
        Verify generic parameters.
        If there is any hazard, raise an error.
        """
        if not generic:
            return {}
        for identifier, generic_type in generic.items():
            if identifier != identifier.upper():
                raise errors.IdentifierError(
                    "Generic keyword should be an uppercase word"
                )
        return generic

    def represented_identifier(self) -> str | None:
        return self._identifier


class AbstractAtomicTransaction(AbstractComponent):
    """
    Represents an atomic transaction consists one or more commands, including
    typical assignable statements, etc.
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
