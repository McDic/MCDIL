import typing

from .errors import IdenfitierCollision


class Identifier:
    """
    Represents a single identifier covers variables,
    namespaces, functions, and even anonymous blocks.
    If there is no parent, then this identifier
    is available on global namespace.
    """

    def __init__(
        self, name: str, parent: typing.Self | None = None, exported: bool = False
    ):
        self._name = name
        self._parents: list["Identifier"] = []
        self._exported = exported
        self._children: dict[str, "Identifier"] = {}
        if parent is not None:
            self.place_on(parent)

    @property
    def name(self):
        return self._name

    def place_on(self, parent: "Identifier"):
        """
        Reserve current identifier on given `parent`.
        """

        if self._name in parent._children:
            if self is not parent._children[self._name]:
                raise IdenfitierCollision(
                    "Identifier %s collided while trying to place on parent %s"
                    % (self._name, parent._name)
                )
            else:  # Connection already exists, silently ignore
                return

        self._parents.append(parent)
        parent._children[self._name] = self
