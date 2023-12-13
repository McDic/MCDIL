"""
Defines several simple global objects in Minecraft.
"""

import typing

from .textjson import TextJson

if typing.TYPE_CHECKING:
    from . import *


class SimpleGlobal:
    """
    Abstract class of all modifyable objects in Minecraft.
    This object does not belong to any player or entity in game.
    """

    RULES: dict[str, typing.Union[set[str], None, type]]
    MODIFY_FORMAT: str

    _cache: dict[str, typing.Self]

    # https://stackoverflow.com/questions/52966866/subclass-with-class-variable-inheritance
    def __init_subclass__(cls) -> None:
        cls._cache = {}

    def __init__(self, name: str):
        self._name = name
        if self._name in type(self)._cache:
            raise ValueError(
                '%s "%s" already exists;'
                % (
                    type(self).__name__,
                    self._name,
                )
            )
        else:
            type(self)._cache[self._name] = self

    @property
    def name(self):
        return self._name

    def __str__(self):
        return self.name

    @classmethod
    def new(cls, name: str) -> typing.Self:
        """
        Use this method to create new one instead of calling constructor directly.
        """
        return cls._cache[name] if name in cls._cache else cls(name)  # type: ignore

    @classmethod
    def check_rule(cls, rule: str, value: typing.Any) -> bool:
        """
        Return if given rule satisfies this object.
        """
        if rule not in cls.RULES:
            return False
        possible_values = cls.RULES[rule]
        if possible_values is None:
            return True
        elif isinstance(possible_values, type):
            return isinstance(value, possible_values)
        else:
            return value in possible_values

    def modify(self, rule: str, value: typing.Any) -> str:
        """
        Return a command which modifies the team.
        """
        if not self.check_rule(rule, value):
            raise ValueError("Given value %s for rule %s are invalid" % (value, rule))
        return self.MODIFY_FORMAT.format(
            name=self.name,
            rule=rule,
            value=("true" if value else "false")
            if isinstance(value, bool)
            else str(value),
        )

    def create(self) -> str:
        """
        Return a command which creates this object.
        """
        raise NotImplementedError

    def remove(self) -> str:
        """
        Return a command which removes this object.
        """
        raise NotImplementedError


class Team(SimpleGlobal):
    """
    Represent a "team" in Minecraft.
    """

    RULES = {
        "collisionRule": {"always", "never", "pushOtherTeams", "pushOwnTeam"},
        "color": {
            "aqua",
            "black",
            "blue",
            "dark_aqua",
            "dark_blue",
            "dark_gray",
            "dark_green",
            "dark_purple",
            "dark_red",
            "gold",
        },
        "deathMessageVisibility": {
            "always",
            "hideForOtherTeams",
            "hideForOwnTeam",
            "never",
        },
        "displayName": None,
        "friendlyFire": {"true", "false"},
        "nametagVisibility": {"always", "hideForOtherTeams", "hideforOwnTeam", "never"},
        "prefix": None,
        "seeFriendlyInvisibles": {"true", "false"},
        "suffix": None,
    }
    MODIFY_FORMAT = "team modify {name} {rule} {value}"

    def __repr__(self) -> str:
        return "Team %s" % (self.name,)

    def create(self) -> str:
        return "team add %s" % (self.name,)

    def empty(self) -> str:
        """
        Return command which truncates the team.
        """
        return "team empty %s" % (self.name,)

    def collision(self, push_my_team: bool, push_other_teams: bool) -> str:
        value: str = {
            (True, True): "always",
            (True, False): "pushOwnTeam",
            (False, True): "pushOtherTeams",
            (False, False): "never",
        }[(push_my_team, push_other_teams)]
        return self.modify("collisionRule", value)

    def color(self, color: str) -> str:
        return self.modify("color", color)

    def display_name(self, display_name: str) -> str:
        """
        Note that this option is different from chat prefix and suffix.
        """
        return self.modify("display_name", display_name)

    def friendly_fire(self, value: bool) -> str:
        return self.modify("friendlyFire", value)

    def name_visibility(
        self, hide_for_my_team: bool, hide_for_other_teams: bool
    ) -> str:
        value: str = {
            (True, True): "never",
            (True, False): "hideForOwnTeam",
            (False, True): "hideForOtherTeams",
            (False, False): "always",
        }[(hide_for_my_team, hide_for_other_teams)]
        return self.modify("nametagVisibility", value)

    def see_friendly_invisibles(self, value: bool) -> str:
        return self.modify("seeFriendlyInvisibles", value)


class ScoreboardObjective(SimpleGlobal):
    """
    Represent a "scoreboard objective" in Minecraft.
    """

    RULES = {"displayname": TextJson, "rendertype": {"hearts", "integral"}}
    MODIFY_FORMAT = "scoreboard objectives modify {name} {rule} {value}"

    def __init__(self, name: str, criteria: str) -> None:
        super().__init__(name)
        self._criteria = criteria

    def __repr__(self) -> str:
        return "Scoreboard Objective %s" % (self.name,)

    def create(self) -> str:
        return "scoreboard objectives add %s %s" % (self.name, self._criteria)

    def remove(self) -> str:
        return "scoreboard objectives remove %s" % (self.name,)

    def display_name(self, display_name: TextJson) -> str:
        return self.modify("displayname", display_name)

    def render_type(self, render_type: typing.Literal["hearts", "integer"]) -> str:
        return self.modify("rendertype", render_type)
