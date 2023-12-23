from .base import AbstractDefinition


class NamespaceDefinition(AbstractDefinition):
    """
    Represents a namespace definition.
    Unlike other definitions, there is no generic here.
    The root of the module is considered as "root namespace".
    """

    def __init__(self, *, identifier: str, **kwargs) -> None:
        super().__init__(identifier=identifier, generic=None, **kwargs)
