import typing


class AbstractComponent:
    """
    Represents an abstract component.
    """

    _cache: dict[str, typing.Self]

    def __init__(self, name: str | None = None) -> None:
        self._name = name
        if self.name in self._cache:
            raise ValueError(
                "Same name '%s' of type %s already exists" % (name, type(self).__name__)
            )
        self._cache[self.name] = typing.cast(typing.Self, self)

    def __init_subclass__(cls) -> None:
        cls._cache = {}

    def get_commands(self) -> list[str]:
        raise NotImplementedError

    @property
    def name(self):
        return self._name


class AbstractAtomicTransaction(AbstractComponent):
    """
    Represents an atomic transaction consists one or more commands.
    """

    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
