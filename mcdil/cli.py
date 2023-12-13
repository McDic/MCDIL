import argparse
from pathlib import Path

from .parse import parse

common_parser = argparse.ArgumentParser()
common_parser.add_argument("--file", "-f", type=Path, required=True)


def cli_parse():
    namespace = common_parser.parse_args()
    with open(namespace.file) as codefile:
        print(parse(codefile.read()).pretty())


def cli_compile():
    raise NotImplementedError
