import typing
from enum import Enum
from enum import auto as enumauto


class CoordinateMode(Enum):
    Absolute = enumauto()  # x
    Relative = enumauto()  # ~x
    Local = enumauto()  # ^x


class Coordinates3D:
    """
    Represents 3D coordinate information in Minecraft.
    For absolute and relative coordinates, `x`, `y`, `z` refers
    to the corresponding axis on Minecraft.
    For local coordinates, `x`, `y`, `z` refers to
    the left side, upper side, front side of the entity.
    """

    PREFIX: typing.Final[dict[CoordinateMode, str]] = {
        CoordinateMode.Absolute: "",
        CoordinateMode.Relative: "~",
        CoordinateMode.Local: "^",
    }

    def __init__(
        self,
        x: typing.Union[int, float],
        y: typing.Union[int, float],
        z: typing.Union[int, float],
        xmode: CoordinateMode = CoordinateMode.Absolute,
        ymode: CoordinateMode = CoordinateMode.Absolute,
        zmode: CoordinateMode = CoordinateMode.Absolute,
    ):
        if abs(y) > pow(2, 10):
            raise ValueError("Too big abs for y = %s" % (y,))
        self._x = x
        self._y = y
        self._z = z

        coordinate_modes: set[CoordinateMode] = {xmode, ymode, zmode}
        if CoordinateMode.Local in coordinate_modes and len(coordinate_modes) > 1:
            raise ValueError("Local and non-Local coordinates are mixed")
        self._xmode = xmode
        self._ymode = ymode
        self._zmode = zmode

    def __str__(self) -> str:
        return "%s%s %s%s %s%s" % (
            self.PREFIX[self._xmode],
            self._x,
            self.PREFIX[self._ymode],
            self._y,
            self.PREFIX[self._zmode],
            self._z,
        )


class Coordinates5D(Coordinates3D):
    """
    Represents 5D coordinate(`x`, `y`, `z`, `x_rotation`, `y_rotation`)
    information in Minecraft.
    """

    def __init__(
        self,
        x: typing.Union[int, float],
        y: typing.Union[int, float],
        z: typing.Union[int, float],
        vertical_rotation: typing.Union[int, float],
        horizontal_rotation: typing.Union[int, float],
        xmode: CoordinateMode = CoordinateMode.Absolute,
        ymode: CoordinateMode = CoordinateMode.Absolute,
        zmode: CoordinateMode = CoordinateMode.Absolute,
        vertical_rotation_mode: CoordinateMode = CoordinateMode.Absolute,
        horizontal_rotation_mode: CoordinateMode = CoordinateMode.Absolute,
    ):
        super().__init__(x, y, z, xmode, ymode, zmode)

        if (
            vertical_rotation_mode is CoordinateMode.Local
            or horizontal_rotation_mode is CoordinateMode.Local
        ):
            raise ValueError("Cannot use Local mode for rotations")
        elif abs(horizontal_rotation) > 180:
            raise ValueError(
                "Too big abs for horizontal rotation = %s" % (horizontal_rotation,)
            )
        elif abs(vertical_rotation) > 90:
            raise ValueError(
                "Too big abs for vertical rotation = %s" % (vertical_rotation,)
            )

        self._horizontal_rotation = horizontal_rotation
        self._vertical_rotation = vertical_rotation
        self._horizontal_rotation_mode = horizontal_rotation_mode
        self._vertical_rotation_mode = vertical_rotation_mode

    def __str__(self) -> str:
        return "%s %s%s %s%s" % (
            super().__str__(),
            self.PREFIX[self._horizontal_rotation_mode],
            self._horizontal_rotation,
            self.PREFIX[self._vertical_rotation_mode],
            self._vertical_rotation,
        )
