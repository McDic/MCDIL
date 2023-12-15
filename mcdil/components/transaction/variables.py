from ..base import AbstractAtomicTransaction


class DirectAlter(AbstractAtomicTransaction):
    """
    Represent a variable's change.
    All `initialization`s and `alter_statement`s goes here.
    """

    def __init__(self, component_name: str, variable_name: str, operator: str) -> None:
        super().__init__(component_name)


class DirectBinaryOperation(AbstractAtomicTransaction):
    """
    Represent a binary operation.
    """
