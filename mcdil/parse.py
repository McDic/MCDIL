from pathlib import Path

from lark import Lark, ParseTree, Transformer

global_mcdil_parser: Lark | None = None


def load_grammar(path: Path | None = None, start: str = "program") -> Lark:
    global global_mcdil_parser
    if global_mcdil_parser is not None:
        return global_mcdil_parser
    path = path or Path(__file__).absolute().parent / "mcdil.lark"
    with open(path, "r") as grammar_file:
        global_mcdil_parser = Lark(
            grammar_file.read(),
            start=start,
            debug=True,
        )
        return global_mcdil_parser


class McDilTransformer(Transformer):
    def program(self, items):
        return []


def parse(code: str) -> ParseTree:
    parsed_tree = load_grammar().parse(code)
    return parsed_tree


if __name__ == "__main__":
    with open("examples/test.mcdil") as test_mcdil:
        parse(test_mcdil.read())
