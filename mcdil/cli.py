import argparse
import enum
from pathlib import Path

from .parser import parse


class CompilationLevel(enum.Enum):
    """
    Enumeration of all compilation levels.
    """

    PARSE = 1
    COMPILE = 2
    FULL = COMPILE


def get_compilation_level(x: str) -> CompilationLevel:
    """
    If `x` can be converted into int, return corresponding level to that int.
    Otherwise, return corresponding level to the string itself.
    """
    try:
        level = int(x)
    except ValueError:
        return CompilationLevel[x.upper()]
    else:
        return CompilationLevel(level)


def perform(path: Path, level: CompilationLevel) -> bool:
    """
    Perform compilation process for given path and level.
    """

    with open(path, "r") as codefile:
        code: str = codefile.read()

    level_num = level.value

    if 1 <= level_num:
        tree = parse(code)
    if 1 == level_num:
        print("=" * 120)
        print(tree.pretty())
        print("=" * 120)
        return True

    # Unsupported branch
    print("This level %s is currently unsupported." % (level.name,))
    return False


def main():
    """
    Main entry of the CLI program.
    """

    # Parse opt-args
    parser = argparse.ArgumentParser(prog="mcdil")
    parser.add_argument(
        "--file",
        "-f",
        nargs="+",
        type=Path,
        required=True,
        help="specify a `.mcdil` file to analyze",
    )
    parser.add_argument(
        "--level",
        "-l",
        type=(lambda lv: get_compilation_level(lv)),
        required=True,
        help="specify a level for compilation process: %s"
        % (", ".join(level.name for level in CompilationLevel),),
    )
    namespace = parser.parse_args()

    for path in namespace.file:
        print("Performing %s process for file %s.." % (namespace.level.name, path))
        if not perform(path, namespace.level):
            exit(1)
