import typing

T = typing.TypeVar("T")
T_PH = typing.TypeVar("T_PH", bool, int, float, str)  # T_PLACEHOLDER


class PlaceHolder(typing.Generic[T_PH]):
    """
    Represent a placeholder of primitive values
    for scoreboard static variable or NBT storage.
    """

    def __init__(self, t: type[T_PH]):
        self._type: type[T_PH] = t

    def copy(self, another: typing.Self) -> str:
        """
        Return a command which copies the value.
        """
        raise NotImplementedError


class ScoreboardGlobalVariable(PlaceHolder[int]):
    """
    Placeholder for scoreboard variable.
    """

    def __init__(self, scoreboard_objective):
        pass
