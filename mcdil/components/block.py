from .base import AbstractComponent


class Block(AbstractComponent):
    """
    Represents a block of the code, contains zero or more transactions.
    This block can contain many blocks as child.
    """

    def __init__(self, name: str | None = None):
        super().__init__(name=name)


class AtomicBlock(Block):
    """
    Represents an atomic block of the code.
    "Atomic" block can be 1-to-1 matched with `.mcfunction` files.
    """

    def __init__(self, name: str | None = None):
        super().__init__(name)
