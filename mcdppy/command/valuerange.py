import typing

T_NUM = typing.TypeVar("T_NUM", int, float)


class ValueRange(typing.Generic[T_NUM]):
    """
    Represent value range in Minecraft.
    This is a generic type for convenient typing.
    """

    @typing.overload
    def __init__(self, t: tuple[T_NUM, T_NUM]):
        ...

    @typing.overload
    def __init__(self, value: T_NUM):
        ...

    @typing.overload
    def __init__(self, minvalue: T_NUM, maxvalue: T_NUM):
        ...

    def __init__(self, *args: typing.Any, **kwargs: typing.Any):
        assert not kwargs
        self._min: typing.Optional[T_NUM] = None
        self._max: typing.Optional[T_NUM] = None
        if len(args) == 1:
            if isinstance(args[0], tuple):
                assert len(args[0]) == 2
                self._min, self._max = args[0]  # Overload #1
            else:
                self._min = self._max = args[0]  # Overload #2
        elif len(args) == 2:
            self._min, self._max = args  # Overload #3
        else:
            raise ValueError(
                "Invalid argument for ValueRange constructor: %s" % (args,)
            )
        assert self._min is not None or self._max is not None

    def __str__(self) -> str:
        return (
            "%s..%s"
            % (
                self._min if self._min is not None else "",
                self._max if self._max is not None else "",
            )
            if self._min != self._max
            else str(self._min)
        )
