import typing
from pathlib import Path

from .. import errors
from ..constants import HARD_KEYWORDS, GenericParameterType


class AbstractComponent:
    """
    Represents an any abstract code component.
    This includes all kind of statements including

    - Function definitions
    - Assignable statements
    - Namespace blocks

    and more.
    """

    AUTHORABLE: typing.ClassVar[bool] = False

    def __init__(
        self,
        *,
        component_name: str | None = None,
        parent: typing.Self | None = None,
        exported: bool = False,
    ) -> None:
        """
        Component name is an identifier to access this,
        can be `None` for anonymous blocks like `while` loops and more.

        Both `parent` and `linked` are accessible identifiers,
        however `linked` is not used for outer name resolution.
        A root of the module is always parent-less component.
        """

        # Literal or inherited properties
        self._component_name: str | None = component_name
        if component_name in HARD_KEYWORDS:
            raise errors.KeywordIdentifier(component_name)
        self._author_name: str | None = None
        self._author_email: str | None = None
        self.exported: typing.Final[bool] = exported

        # Graph properties
        self._childs: list[typing.Self] = []
        self._raw_visible_identifiers_cache: dict[str, typing.Self] = {}

        # Parent
        self._parent: typing.Self | None = parent
        if self._parent is not None:
            self._parent.register_link(self)

    @typing.final
    def register_link(self, child: typing.Self):
        """
        Register given `child` as a link to this component.
        Duplicated registration will cause an error.
        """
        self._childs.append(child)
        if (child_identifier := child.represented_identifier()) is not None:
            if child_identifier in self._raw_visible_identifiers_cache:
                raise errors.IdenfitierCollision(child_identifier)
            self._raw_visible_identifiers_cache[child_identifier] = child

    def represented_identifier(self) -> str | None:
        """
        An identifier represent this component.
        If this component is something like variable definition,
        function definition, namespace block, etc, then
        this component should return a proper identifier string.
        If the result of this method is `None`,
        then this component does not have any identifier.
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

    def get_author(self, make_cache: bool = False) -> tuple[str, str] | None:
        """
        Get author name and email. If no author is available, return `None`.
        This method also does caching if you want.
        """
        if self._author_name is not None and self._author_email is not None:
            return (self._author_name, self._author_email)
        elif self._parent is None:
            return None
        else:
            author_info = self._parent.get_author(make_cache=make_cache)
            if author_info is not None and make_cache:
                self._author_name, self._author_email = author_info
            return author_info

    def find_by_identifiers(
        self, *namespaced_identifier: str, inner_propagation_started: bool = False
    ) -> typing.Self:
        """
        Try to find correct component with given namespaced identifiers.
        This tried to find given identifier from all ancestors,
        therefore in some cases performance may be slow.
        """
        if not namespaced_identifier:  # No identifier == self
            return self

        try:  # If directly found from children, try with no backward propagation
            if namespaced_identifier[0] in self._raw_visible_identifiers_cache:
                child = self._raw_visible_identifiers_cache[namespaced_identifier[0]]
                # Search only when either
                # inner propagation is not start yet, or child is exported
                if not inner_propagation_started or child.exported:
                    return child.find_by_identifiers(
                        *namespaced_identifier[1:], inner_propagation_started=True
                    )
        except errors.IdentifierNotFound:
            pass

        # Go to upper identifier and try again, if able to move
        if self._parent is not None and not inner_propagation_started:
            return self._parent.find_by_identifiers(*namespaced_identifier)
        else:
            raise errors.IdentifierNotFound("::".join(namespaced_identifier))


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
    """

    def __init__(
        self,
        *,
        identifier: str,
        generic: GENERIC_PARAMETERS | None = None,
        description: str = "",
        **kwargs,
    ) -> None:
        """
        If `generic` is an empty dict, then this object
        is considered as non-generic object.
        """
        super().__init__(component_name=identifier, **kwargs)
        self._generic: GENERIC_PARAMETERS = self._verify_generic_parameters(generic)
        self._description: str = description

    def set_description(self, description: str):
        """
        Set this component's description, if not set.
        """
        if self._description:
            raise errors.DescriptionAlreadySet
        self._description = description

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
