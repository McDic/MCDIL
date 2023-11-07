"""
Provide misc utilities for many stuffs.
"""

import typing
from copy import deepcopy
from dataclasses import dataclass


@dataclass(slots=True)  # type: ignore
class Version:
    """
    Represent a semantic version.
    """

    major: int
    minor: int
    patch: int

    def __init__(self, *args):
        if len(args) == 1:
            if isinstance(args[0], str):
                major, minor, patch = [int(c) for c in args[0].split(".")]
            elif isinstance(args[0], float):
                rounded = str(round(args[0], 4))
                major, minor = [int(c) for c in rounded.split(".")]
                patch = 0
            else:
                raise ValueError("Unsupported type(%s) parameter" % (type(args[0]),))

        elif 2 <= len(args) <= 3:
            for arg in args:
                assert isinstance(arg, int)
            major = args[0]
            minor = args[1]
            patch = args[2] if len(args) >= 3 else 0

        else:
            raise ValueError("Invalid number of parameters are passed.")

        assert major >= 0 and minor >= 0 and patch >= 0

    def __eq__(self, other) -> bool:
        return isinstance(other, type(self)) and (
            self.major,
            self.minor,
            self.patch,
        ) == (
            other.major,
            other.minor,
            other.patch,
        )

    def __lt__(self, other) -> bool:
        return isinstance(other, type(self)) and (
            self.major,
            self.minor,
            self.patch,
        ) < (
            other.major,
            other.minor,
            other.patch,
        )

    def __le__(self, other) -> bool:
        return self == other or self < other

    def __str__(self):
        return "Version (%d, %d, %d)" % (self.major, self.minor, self.patch)


DefaultMinecraftVersion: typing.Final[Version] = Version(1, 20, 2)


def writeline(ostream: typing.TextIO, line: str):
    """
    Convenient method to write `line` to `ostream` with extra newline.
    """
    ostream.write(line)
    ostream.write("\n")


def modify_dict(
    original: dict, *args: dict, raise_on_conflict: bool = True, deep: bool = False
) -> None:
    """
    Apply modification on `original` with `args`.
    If `raise_on_conflict` is `True` then raise an error on any conflict.
    """
    for d in args:
        for key, value in d.items():
            if key not in original:
                original[key] = value if not deep else deepcopy(value)
            elif isinstance(original[key], dict) and isinstance(value, dict):
                modify_dict(
                    original[key], value, raise_on_conflict=raise_on_conflict, deep=deep
                )
            elif original[key] == value:
                pass
            elif raise_on_conflict:
                raise ValueError("Dict conflict happened")


def merge_dict(*args: dict, raise_on_conflict: bool = True, deep: bool = False) -> dict:
    """
    Merge all dicts but performs shallow copy on non-primitive objects.
    If `raise_on_conflict` is `True` then raise an error on any conflict.
    """
    result: dict = {}
    modify_dict(result, *args, raise_on_conflict=raise_on_conflict, deep=deep)
    return result
