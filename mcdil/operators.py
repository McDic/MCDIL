import enum


class Operator(enum.Enum):
    ADD = "+"
    SUB = "-"
    MUL = "*"
    DIV = "/"
    MOD = "%"
    EQ = "=="
    NE = "!="
    LT = "<"
    LE = "<="
    GT = ">"
    GE = ">="
    ASSIGN = "="
    ASSIGN_ADD = "+="
    ASSIGN_SUB = "-="
    ASSIGN_MUL = "*="
    ASSIGN_DIV = "/="
    ASSIGN_MOD = "%="
    AND = "&"
    OR = "|"
    XOR = "^"
    NOT = "~"
