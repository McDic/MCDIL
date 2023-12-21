import typing


class AbstractComponent:
    """
    Represents an abstract code component.
    """

    def __init__(self, component_name: str) -> None:
        self._component_name = component_name

    def get_commands(self) -> list[str]:
        """
        Get list of commands that implements this component.
        Some components may not implement this behaviour
        by returning an empty list.
        """
        return []

    @property
    def component_name(self):
        return self._component_name


class AbstractAtomicTransaction(AbstractComponent):
    """
    Represents an atomic transaction consists one or more commands.
    """

    def __init__(self, component_name: str) -> None:
        super().__init__(component_name)
