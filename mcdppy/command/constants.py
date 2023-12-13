import enum


class Gamemode(enum.Enum):
    """
    Enumerations of all possible gamemodes.
    """

    Survival = "survival"
    Creative = "creative"
    Adventure = "adventure"
    Spectator = "spectator"


class SortingMode(enum.Enum):
    """
    Enumerations of all possible sorting modes in a target selector.
    """

    Nearest = "nearest"
    Furthest = "furthest"
    Random = "random"
    Arbitrary = "arbitrary"
