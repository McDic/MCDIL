import typing
from pathlib import Path

from .. import errors
from ..constants import HARD_KEYWORDS, GenericParameterType


class AbstractComponent:
    """
    Represents an any abstract code component.
    This includes all kind of statements including

    - function definitions
    - assignable statements
    - namespace block

    and more.
    """

    AUTHORABLE: typing.ClassVar[bool] = False

    def __init__(
        self,
        *,
        component_name: str | None = None,
        module_path: Path | str,
        parent: typing.Self | None = None,
    ) -> None:
        # Literal or inherited properties
        self._component_name: str | None = component_name
        self._module_path: Path | str = module_path
        self._author_name: str | None = None
        self._author_email: str | None = None

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

    def set_author(self, name: str, email: str) -> None:
        """
        Try to set an author. If already set, raise an error.
        """
        if not self.AUTHORABLE:
            raise errors.NotAuthorable()
        elif self._author_name is not None or self._author_email is not None:
            raise errors.AuthorAlreadySet(name=name, email=email)
        self._author_name = name
        self._author_email = name


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
        super().__init__(component_name=identifier, **kwargs)
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
        return self._component_name


class AbstractAtomicTransaction(AbstractComponent):
    """
    Represents an atomic transaction consists one or more commands, including
    typical assignable statements, etc.
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
