import os
import typing
from pathlib import Path

from ..command import Command
from ..utils import writeline


class AbstractCommandSequence:
    """
    Represents sequence of commands.
    """

    def generate(self) -> typing.Generator[str, None, None]:
        raise NotImplementedError


class AbstractFunction:
    """
    Abstract class of all functions.
    """

    def __init__(self, *commands: typing.Union[Command, AbstractCommandSequence]):
        self._commands = list(commands)

    def write(self, path: Path):
        """
        Write all commands used in this function to given `path`.
        Normally you will not explicitly call this,
        instead bigger components will automatically implicitly call this.
        """
        if path.is_dir():
            raise OSError("Given path %s is a directory" % (path,))
        elif path.exists():
            os.remove(path)

        with open(path, "w") as mcf_file:
            for stuff in self._commands:
                if isinstance(stuff, Command):
                    writeline(mcf_file, stuff.command)
                elif isinstance(stuff, AbstractCommandSequence):
                    pass
                else:
                    raise TypeError(
                        "Invalid command stuff type(%s) found" % (type(stuff),)
                    )
