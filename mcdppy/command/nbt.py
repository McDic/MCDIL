import re
import typing
from enum import Enum
from enum import auto as enumauto

T = typing.TypeVar("T")

PRIMITIVE_LITERAL_NBT_TYPE = typing.Union[int, float, bool, str, bytearray]
LITERAL_NBT_TYPE = typing.Union[
    PRIMITIVE_LITERAL_NBT_TYPE,
    typing.Sequence["LITERAL_NBT_TYPE"],
    typing.Mapping[str, "LITERAL_NBT_TYPE"],
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
    POSSIBLE_TYPES = typing.Union[
        PRIMITIVE_LITERAL_NBT_TYPE,
        typing.Sequence[typing.Union["POSSIBLE_TYPES", T]],
        typing.Mapping[str, typing.Union["POSSIBLE_TYPES", T]],
    ]
    INT_INDEX_SYNTAX: typing.Final[re.Pattern] = re.compile(r"^\[[0-9]+\]$")

    # Member variables which is needed to declared here because of type aliases
    _value: POSSIBLE_TYPES[typing.Self]
    _type: IndividualNBTTypes

    def __init__(
        self,
        value: typing.Union[POSSIBLE_TYPES[typing.Self], LITERAL_NBT_TYPE, typing.Self],
        type_: typing.Optional[IndividualNBTTypes] = None,
        parents: typing.Optional[dict[typing.Union[int, str], typing.Self]] = None,
    ):
        """
        If `type_` is `None`, then it will automatically
        choose the appropriate type. Otherwise, it will check
        if the type of given `value` and `type_` are actually matching.
        """
        if type_ is None:
            if isinstance(value, NBT):  # Copying
                self._type = value._type
            elif isinstance(value, bool):
                self._type = IndividualNBTTypes.Bool
            elif isinstance(value, int):
                self._type = IndividualNBTTypes.Int
            elif isinstance(value, float):
                self._type = IndividualNBTTypes.Double
            elif isinstance(value, str):
                self._type = IndividualNBTTypes.Float
            elif isinstance(value, list):
                self._type = IndividualNBTTypes.List
            elif isinstance(value, dict):
                self._type = IndividualNBTTypes.Compound
            elif isinstance(value, bytearray):
                self._type = IndividualNBTTypes.ByteArray
            else:
                raise ValueError(
                    "Cannot automatically deduce the type from given value type(%s)"
                    % (type(value),)
                )
        else:
            if isinstance(value, NBT) and type_ is not value._type:
                raise ValueError(
                    "You passed different type for NBT: %s vs %s" % (value._type, type_)
                )
            self._type = type_

        self._value = self.clean(value)
        self._parents: dict[str, typing.Self] = {}  # {access_index: NBT}
        self.add_parents(parents or {})

    def is_primitive(self) -> bool:
        """
        Return if this NBT is primitive.
        """
        return self._type in {
            IndividualNBTTypes.Bool,
            IndividualNBTTypes.Byte,
            IndividualNBTTypes.Short,
            IndividualNBTTypes.Int,
            IndividualNBTTypes.Long,
            IndividualNBTTypes.Float,
            IndividualNBTTypes.Double,
            IndividualNBTTypes.String,
        }

    def is_list(self):
        """
        Return if this NBT is list type.
        """
        return self._type in {
            IndividualNBTTypes.List,
            IndividualNBTTypes.ByteArray,
            IndividualNBTTypes.IntArray,
            IndividualNBTTypes.LongArray,
        }

    def add_parents(self, parents: dict[typing.Union[int, str], typing.Self]):
        """
        Add parents with checking type validity.
        """
        for index, parent in parents.items():
            if index in self._parents:
                raise ValueError(
                    "Parent index(%s) for this NBT already exists" % (index,)
                )
            elif isinstance(index, int):
                if not parent.is_list():
                    raise ValueError("Parent NBT type must be list for int index")
                elif {
                    IndividualNBTTypes.List: self._type,
                    IndividualNBTTypes.ByteArray: IndividualNBTTypes.Byte,
                    IndividualNBTTypes.Int: IndividualNBTTypes.Int,
                    IndividualNBTTypes.LongArray: IndividualNBTTypes.Long,
                }[parent._type] is not self._type:
                    raise ValueError(
                        "Parent type is typed list(%s) but child type is %s"
                        % (parent._type, self._type)
                    )
                self._parents["[%d]" % (index,)] = parent
            elif isinstance(index, str):
                if parent._type is not IndividualNBTTypes.Compound:
                    raise ValueError("Parent NBT type must be compound for str index")
                self._parents[index] = parent
            else:
                raise ValueError(
                    "Unsupported; Parent NBT type is %s and index is %s (type %s)"
                    % (parent._type, index, type(index))
                )

    def __str__(self) -> str:
        match self._type:
            case IndividualNBTTypes.Bool:
                assert isinstance(self._value, bool)
                return "true" if self._value else "false"
            case IndividualNBTTypes.Byte:
                assert isinstance(self._value, int)
                return "%db" % (self._value,)
            case IndividualNBTTypes.Short:
                assert isinstance(self._value, int)
                return "%ds" % (self._value,)
            case IndividualNBTTypes.Int:
                assert isinstance(self._value, int)
                return "%d" % (self._value,)
            case IndividualNBTTypes.Long:
                assert isinstance(self._value, int)
                return "%dL" % (self._value,)
            case IndividualNBTTypes.Float:
                assert isinstance(self._value, float)
                return "%.6gf" % (self._value,)
            case IndividualNBTTypes.Double:
                assert isinstance(self._value, float)
                return "%.6gD" % (self._value,)
            case IndividualNBTTypes.String:
                assert isinstance(self._value, str)
                return self._value
            case IndividualNBTTypes.List:
                assert isinstance(self._value, typing.Sequence)
                return "[" + ",".join(str(subvalue) for subvalue in self._value) + "]"
            case IndividualNBTTypes.Compound:
                assert isinstance(self._value, dict)
                return (
                    "{"
                    + ",".join(
                        '"%s":%s' % (key, subvalue)
                        for key, subvalue in self._value.items()
                    )
                    + "}"
                )
            case IndividualNBTTypes.ByteArray:
                assert isinstance(self._value, typing.Sequence)
                return "[B;" + ",".join(str(x) for x in self._value) + "]"
            case IndividualNBTTypes.IntArray:
                assert isinstance(self._value, typing.Sequence)
                return "[I;" + ",".join(str(x) for x in self._value) + "]"
            case IndividualNBTTypes.LongArray:
                assert isinstance(self._value, typing.Sequence)
                return "[L;" + ",".join(str(x) for x in self._value) + "]"
        raise NotImplementedError("Not implemented for NBT type %s" % (self._type,))

    def clean(
        self,
        value: typing.Union[POSSIBLE_TYPES[typing.Self], LITERAL_NBT_TYPE, typing.Self],
    ) -> POSSIBLE_TYPES[typing.Self]:
        """
        Performs type check and initialize corresponding child objects.
        """
        if isinstance(value, NBT):
            if value._type is not self._type:
                raise ValueError(
                    "NBT type(%s) is not equal to given type_(%s)"
                    % (value._type, self._type)
                )
            return value._value  # type: ignore # maybe mypy bug

        if self.is_primitive():
            target_primitive_type = {
                IndividualNBTTypes.Bool: bool,
                IndividualNBTTypes.Byte: int,
                IndividualNBTTypes.Short: int,
                IndividualNBTTypes.Int: int,
                IndividualNBTTypes.Long: int,
                IndividualNBTTypes.Float: float,
                IndividualNBTTypes.Double: float,
                IndividualNBTTypes.String: str,
            }[self._type]
            if not isinstance(value, target_primitive_type):
                raise TypeError(
                    "Invalid value %s given for primitive NBT %s" % (value, self._type)
                )
            return value  # type: ignore # maybe mypy bug

        elif self.is_list():
            if not isinstance(value, (list, bytearray)):
                raise TypeError("Invalid value %s given for NBT list" % (value,))
            subtype: typing.Optional[IndividualNBTTypes] = {
                IndividualNBTTypes.List: None,
                IndividualNBTTypes.ByteArray: IndividualNBTTypes.Byte,
                IndividualNBTTypes.IntArray: IndividualNBTTypes.Int,
                IndividualNBTTypes.LongArray: IndividualNBTTypes.Long,
            }[self._type]
            return [
                type(self)(subvalue, type_=subtype, parents={i: self})
                for i, subvalue in enumerate(value)
            ]

        elif self._type is IndividualNBTTypes.Compound:
            if not isinstance(value, dict):
                raise TypeError("Invalid value %s given for NBT compound" % (value,))
            return {
                key: (
                    type(self)(subvalue, parents={key: self})
                    if not isinstance(subvalue, type(self))
                    else subvalue
                )
                for key, subvalue in value.items()
            }

        else:
            raise ValueError("Unsupported type_(%s) given" % (self._type,))

    def __getitem__(self, key: typing.Union[str, int]) -> typing.Self:
        if self.is_primitive():
            raise ValueError("Cannot index for primitive NBT types")
        elif self.is_list():
            if not isinstance(key, int):
                raise ValueError("Invalid key %s for accessing child" % (key,))
            assert isinstance(self._value, list)
            return self._value[key]
        elif self._type is IndividualNBTTypes.Compound:
            if not isinstance(key, str):
                raise ValueError("Invalid key %s for accessing child" % (key,))
            assert isinstance(self._value, dict)
            return self._value[key]
        else:
            raise ValueError("Unsupported NBT type %s" % (self._type,))
