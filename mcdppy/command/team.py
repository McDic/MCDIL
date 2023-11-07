import typing


class Team:
    """
    Represent "team" in Minecraft.
    Note that `/team join` and `/team leave` are not supported in this class.
    To do that, use methods from target selectors instead.
    """

    _cache: dict[str, typing.Self] = {}

    def __init__(self, name: str):
        self._name = name
        if self._name in type(self)._cache:
            raise ValueError('Team "%s" already exists;' % (self._name,))
        else:
            type(self)._cache[self._name] = self

    @property
    def name(self):
        return self._name

    @classmethod
    def get_team(cls, name: str) -> typing.Self:
        """
        Use this method to create a team instead of calling constructor directly.
        """
        return cls._cache[name] if name in cls._cache else cls(name)  # type: ignore

    def create(self) -> str:
        """
        Return command which creates the team.
        """
        return "team add %s" % (self.name,)

    def empty(self) -> str:
        """
        Return command which truncates the team.
        """
        return "team empty %s" % (self.name,)
