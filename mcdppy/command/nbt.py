import typing
from enum import Enum
from enum import auto as enumauto

T = typing.TypeVar("T")

PRIMITIVE_LITERAL_NBT_TYPE = typing.Union[int, float, bool, str, bytearray]
LITERAL_NBT_TYPE = typing.Union[
    PRIMITIVE_LITERAL_NBT_TYPE, list["LITERAL_NBT_TYPE"], dict[str, "LITERAL_NBT_TYPE"]
]


class IndividualNBTTypes(Enum):
    """
    Enumeration of individual NBT element's types.
    https://minecraft.fandom.com/wiki/NBT_format
    """

    Bool = enumauto()
    Byte = enumauto()
    Short = enumauto()
    Int = enumauto()
    Long = enumauto()
    Float = enumauto()
    Double = enumauto()
    String = enumauto()
    List = enumauto()
    Compound = enumauto()
    ByteArray = enumauto()
    IntArray = enumauto()
    LongArray = enumauto()


class NBT:
    """
    Represents any NBT, which could be used for entity or `/data`.
    - Since there are way too many NBT attributes,
    I don't check if specific attributes are actually valid or not.
    - All non-primitive NBT values do not have any primitive values inside,
    instead all primitives are wrapped as single NBT object for their child.
    - Reusing same NBT will not actually clone the internal values,
    so be cautious with it.
    - All NBT arrays store values under another NBT child,
    instead of storing an array of primitive values directly.
    """

    # Type helpers
    POSSIBLE_TYPES = typing.Union[PRIMITIVE_LITERAL_NBT_TYPE, list[T], dict[str, T]]

    # Member variables which is needed to declared here because of type aliases
    _value: POSSIBLE_TYPES[typing.Self]

    def __init__(
        self,
        value: typing.Union[POSSIBLE_TYPES[typing.Self], LITERAL_NBT_TYPE, typing.Self],
        type_: typing.Optional[IndividualNBTTypes] = None,
        parent: typing.Optional[typing.Self] = None,
    ):
        """
        If `type_` is `None`, then it will automatically
        choose the appropriate type. Otherwise, it will check
        if the type of given `value` and `type_` are actually matching.
        """
        candidate_type: IndividualNBTTypes = IndividualNBTTypes.Bool
        if type_ is None:
            if isinstance(value, NBT):  # Copying
                candidate_type = value._type
            elif isinstance(value, bool):
                candidate_type = IndividualNBTTypes.Bool
            elif isinstance(value, int):
                candidate_type = IndividualNBTTypes.Int
            elif isinstance(value, float):
                candidate_type = IndividualNBTTypes.Double
            elif isinstance(value, str):
                candidate_type = IndividualNBTTypes.Float
            elif isinstance(value, list):
                candidate_type = IndividualNBTTypes.List
            elif isinstance(value, dict):
                candidate_type = IndividualNBTTypes.Compound
            elif isinstance(value, bytearray):
                candidate_type = IndividualNBTTypes.ByteArray
            else:
                raise ValueError(
                    "Cannot automatically deduce the type from given value type(%s)"
                    % (type(value),)
                )
        else:
            candidate_type = type_
            if isinstance(value, NBT) and candidate_type is not value._type:
                raise ValueError(
                    "You passed different type for NBT: %s vs %s"
                    % (value._type, candidate_type)
                )

        self._value = self.clean(value, candidate_type)
        self._type: IndividualNBTTypes = candidate_type
        self._parent: typing.Optional[typing.Self] = parent
        self._path_cache: str = self.search_path(parent, self)

    def __str__(self) -> str:
        match self._type:
            case IndividualNBTTypes.Bool:
                return "true" if self._value else "false"
            case IndividualNBTTypes.Byte:
                return "%db" % (typing.cast(int, self._value),)
            case IndividualNBTTypes.Short:
                return "%ds" % (typing.cast(int, self._value),)
            case IndividualNBTTypes.Int:
                return "%d" % (typing.cast(int, self._value),)
            case IndividualNBTTypes.Long:
                return "%dL" % (typing.cast(int, self._value),)
            case IndividualNBTTypes.Float:
                return "%.6gf" % (typing.cast(float, self._value),)
            case IndividualNBTTypes.Double:
                return "%.6gD" % (typing.cast(float, self._value),)
            case IndividualNBTTypes.String:
                assert isinstance(self._value, str)
                return self._value
            case IndividualNBTTypes.List:
                assert isinstance(self._value, typing.Iterable)
                return "[" + ",".join(str(subvalue) for subvalue in self._value) + "]"
            case IndividualNBTTypes.Compound:
                assert isinstance(self._value, dict)
                return (
                    "{"
                    + ",".join(
                        "%s:%s" % (key, subvalue)
                        for key, subvalue in self._value.items()
                    )
                    + "}"
                )
            case IndividualNBTTypes.ByteArray:
                assert isinstance(self._value, typing.Iterable)
                return "[B;" + ",".join(str(x) for x in self._value) + "]"
            case IndividualNBTTypes.IntArray:
                assert isinstance(self._value, typing.Iterable)
                return "[I;" + ",".join(str(x) for x in self._value) + "]"
            case IndividualNBTTypes.LongArray:
                assert isinstance(self._value, typing.Iterable)
                return "[L;" + ",".join(str(x) for x in self._value) + "]"
        raise NotImplementedError("Not implemented for NBT type %s" % (self._type,))

    def __getitem__(self, key: typing.Union[str, int]):
        key = key if isinstance(key, str) else "[%d]" % (key,)

    @classmethod
    def search_path(
        cls, parent: typing.Optional[typing.Self], child: typing.Self
    ) -> str:
        """
        Find a path of child from direct parent.
        This method uses `is` operator for here.
        Note that this should not be called explicitly as cache
        will be stored internally on calling constructor.
        """
        if parent is None:  # Child is root
            return ""
        elif isinstance(parent._value, (int, float, bool, str)):
            raise ValueError("Parent is primitive NBT, which does not have any child")
        elif isinstance(parent._value, list):
            for i, candidate_child in enumerate(parent._value):
                if candidate_child is child:
                    return "[%d]" % (i,)
            else:
                raise ValueError("Parent's list does not have the given child")
        elif isinstance(parent._value, dict):
            for key, candidate_child in parent._value.items():
                if candidate_child is child:
                    return key
            else:
                raise ValueError("Parent's compound does not have the given child")
        else:
            raise ValueError("Invalid parent value type %s" % (type(parent._value),))

    def clean(
        self,
        value: typing.Union[POSSIBLE_TYPES[typing.Self], LITERAL_NBT_TYPE, typing.Self],
        type_: IndividualNBTTypes,
    ) -> POSSIBLE_TYPES[typing.Self]:
        """
        Performs type check and initialize corresponding child objects.
        """
        if isinstance(value, NBT):
            if value._type is not type_:
                raise ValueError(
                    "NBT type(%s) is not equal to given type_(%s)"
                    % (value._type, type_)
                )
            return value._value  # type: ignore # maybe mypy bug

        match type_:
            # Primitive types
            case (
                IndividualNBTTypes.Bool
                | IndividualNBTTypes.Byte
                | IndividualNBTTypes.Short
                | IndividualNBTTypes.Int
                | IndividualNBTTypes.Long
                | IndividualNBTTypes.Float
                | IndividualNBTTypes.Double
                | IndividualNBTTypes.String
            ):
                target_primitive_type = {
                    IndividualNBTTypes.Bool: bool,
                    IndividualNBTTypes.Byte: int,
                    IndividualNBTTypes.Short: int,
                    IndividualNBTTypes.Int: int,
                    IndividualNBTTypes.Long: int,
                    IndividualNBTTypes.Float: float,
                    IndividualNBTTypes.Double: float,
                    IndividualNBTTypes.String: str,
                }[type_]
                if not isinstance(value, target_primitive_type):
                    raise TypeError(
                        "Invalid value %s given for primitive NBT %s" % (value, type_)
                    )
                return value  # type: ignore # maybe mypy bug

            # Lists
            case (
                IndividualNBTTypes.List
                | IndividualNBTTypes.ByteArray
                | IndividualNBTTypes.IntArray
                | IndividualNBTTypes.LongArray
            ):
                if not isinstance(value, (list, bytearray)):
                    raise TypeError("Invalid value %s given for NBT list" % (value,))
                subtype: typing.Optional[IndividualNBTTypes] = {
                    IndividualNBTTypes.List: None,
                    IndividualNBTTypes.ByteArray: IndividualNBTTypes.Byte,
                    IndividualNBTTypes.IntArray: IndividualNBTTypes.Int,
                    IndividualNBTTypes.LongArray: IndividualNBTTypes.Long,
                }[type_]
                return [
                    type(self)(subvalue, type_=subtype, parent=self)
                    for subvalue in value
                ]

            # Compound
            case IndividualNBTTypes.Compound:
                if not isinstance(value, dict):
                    raise TypeError(
                        "Invalid value %s given for NBT compound" % (value,)
                    )
                return {
                    key: (
                        type(self)(subvalue, parent=self)
                        if not isinstance(subvalue, type(self))
                        else subvalue
                    )
                    for key, subvalue in value.items()
                }

            # Unsupported
            case _:
                raise ValueError("Unsupported type_(%s) given" % (type_,))

    def get_full_path(self) -> str:
        """
        Get the full path of this NBT.
        Note that `path.[index]` is legal in Minecraft.
        """
        paths: list[str] = []
        # mypy bug: https://github.com/python/mypy/issues/16418
        current: typing.Optional[typing.Self] = self  # type: ignore
        while current is not None and current._path_cache:
            paths.append(current._path_cache)
            current = current._parent
        return ".".join(reversed(paths))
