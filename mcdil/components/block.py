from .base import AbstractAtomicTransaction, AbstractComponent


class Block(AbstractComponent):
    """
    Represents a block of the code, contains zero or more transactions.
    This block can contain many blocks as child.
    """

    def __init__(self, component_name: str):
        super().__init__(component_name)
        self.transactions: list[AbstractAtomicTransaction] = []


class AtomicBlock(Block):
    """
    Represents an atomic block of the code.
    "Atomic" block can be 1-to-1 matched with `.mcfunction` files.
    """

    def __init__(self, component_name: str):
        super().__init__(component_name)
