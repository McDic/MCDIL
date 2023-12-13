import typing
from copy import deepcopy
from dataclasses import dataclass

from ..utils import merge_dict, modify_dict
from .constants import Gamemode, SortingMode
from .nbt import NBT
from .sgo import Team
from .valuerange import ValueRange

if typing.TYPE_CHECKING:
    from . import *


T = typing.TypeVar("T")
T_ADVANCEMENT = typing.Union[bool, dict[str, "T_ADVANCEMENT"]]


def _keep_int_and_float(v) -> typing.Union[int, float]:
    """
    Utility function to convert non-(`int`, `float`) types to float.
    """
    if isinstance(v, (int, float)):
        return v
    else:
        return float(v)


def _single_strize_advancement(v: T_ADVANCEMENT) -> str:
    """
    Recursive utility function to strize advancement conditions.
    """
    if isinstance(v, bool):
        return "true" if v else "false"
    else:
        return (
            "{"
            + ",".join(
                "%s=%s" % (key, _single_strize_advancement(value))
                for key, value in v.items()
            )
            + "}"
        )


class TargetSelector:
    """
    Represents target selector. This class is immutable, which means
    you always get a new object when chaining conditions.
    Therefore it is better to cache some selectors or aggregate
    conditions as much as you can to prevent performance
    issues in case you are using same selector a lot.
    See: https://minecraft.fandom.com/wiki/Target_selectors
    """

    @dataclass(slots=True)
    class ConditionInfo(typing.Generic[T]):
        """
        Dataclass for condition information.
        """

        primary_type: typing.Callable[
            [typing.Any], T
        ]  # Other types given will be automatically casted
        equality_duplicatable: bool = False  # condition=value1,condition=value2
        negatable: bool = False  # condition=!value

        # Stringize function called for all conditions in same category.
        # If set, then this function is passed on merge + duplication.
        merge_strize: typing.Optional[typing.Callable[[list[T]], str]] = None

    AVAILABLE_CONDITIONS: typing.Final[dict[str, ConditionInfo]] = {
        "x": ConditionInfo(_keep_int_and_float),
        "y": ConditionInfo(_keep_int_and_float),
        "z": ConditionInfo(_keep_int_and_float),
        "distance": ConditionInfo(ValueRange),  # float
        "dx": ConditionInfo(_keep_int_and_float),
        "dy": ConditionInfo(_keep_int_and_float),
        "dz": ConditionInfo(_keep_int_and_float),
        "x_rotation": ConditionInfo(ValueRange),  # float
        "y_rotation": ConditionInfo(ValueRange),  # float
        "scores": ConditionInfo(
            dict,  # {score_name: ValueRange}
            equality_duplicatable=True,
            merge_strize=(
                lambda score_conditions: "{"
                + ",".join(
                    "%s=%s" % (score_name, score_valuerange)
                    for score_name, score_valuerange in merge_dict(
                        *score_conditions
                    ).items()
                )
                + "}"
            ),
        ),
        "name": ConditionInfo(
            (lambda team: Team(team) if not isinstance(team, Team) else team),
            equality_duplicatable=False,
            negatable=True,
        ),
        "tag": ConditionInfo(
            str,
            equality_duplicatable=True,
            negatable=True,
        ),
        "team": ConditionInfo(
            Team,
            equality_duplicatable=False,
            negatable=True,
        ),
        "type": ConditionInfo(str, equality_duplicatable=False, negatable=True),
        "predicate": ConditionInfo(str, equality_duplicatable=True, negatable=True),
        "nbt": ConditionInfo(NBT, equality_duplicatable=True, negatable=True),
        "level": ConditionInfo(ValueRange),
        "gamemode": ConditionInfo(Gamemode, equality_duplicatable=False),
        "advancements": ConditionInfo(
            dict,  # {advancement_name: (bool or {criteria: bool})}
            equality_duplicatable=True,
            merge_strize=(
                lambda advancement_conditions: "{%s}"
                % (_single_strize_advancement(merge_dict(*advancement_conditions)),)
            ),
        ),
        "limit": ConditionInfo(int),
        "sort": ConditionInfo(SortingMode),
    }

    def __init__(
        self,
        main_target: typing.Literal["@p", "@r", "@a", "@e", "@s"],
    ):
        self._main_target = main_target
        self._conditions: dict[
            tuple[str, bool], typing.Any
        ] = {}  # {(condition_name, negated): value}

    def __str__(self) -> str:
        condition_str_list: list[str] = []
        raise NotImplementedError
        return self._main_target + (
            "" if not condition_str_list else f"[{','.join(condition_str_list)}]"
        )

    @classmethod
    def process_value(cls, name: str, value: typing.Any) -> typing.Any:
        return cls.AVAILABLE_CONDITIONS[name].primary_type(value)

    # =========================================================================
    # Common condition managements

    def _set_condition(
        self, name: str, value: typing.Any, negated: bool = False
    ) -> typing.Self:
        """
        Try to set condition with `value` on given `name`.
        If it is already set, raise an error.
        Use this when the given condition always should be unique,
        `x=blabla`, `dx=blabla`, or ``
        This method is internally modifying states therefore not safe to call.
        """
        condition = (name, negated)
        negated_condition = (name, not negated)
        if negated and not self.AVAILABLE_CONDITIONS[name].negatable:
            raise ValueError('You can\'t negate on condition "%s"' % (name,))
        elif (
            condition not in self._conditions
            and negated_condition not in self._conditions
        ):
            self._conditions[condition] = self.process_value(name, value)
        else:
            raise ValueError(
                "You tried to set same condition "
                '"%s" multiple times(not considering negation)' % (name,)
            )
        return self

    def _append_condition(
        self, name: str, value: typing.Any, negated: bool = False
    ) -> typing.Self:
        """
        Append new condition with `value` on given `name`.
        Use this when the given condition maintains list of values
        which is not needed to be compressed in one argument,
        `nbt={...}`, `tag=blabla`, or `name=!blabla` for examples.
        Note that there is no value duplication checks, so you need to be careful.
        This method internally modifies the state therefore not safe to call.
        """
        condition = (name, negated)
        if negated and not self.AVAILABLE_CONDITIONS[name].negatable:
            raise ValueError('You can\'t negate on condition "%s"' % (name,))
        elif (
            not negated
            and condition in self._conditions
            and not self.AVAILABLE_CONDITIONS[name].equality_duplicatable
        ):
            raise ValueError('Condition "%s" is not equality-duplicatable' % (name,))

        if condition not in self._conditions:
            self._conditions[condition] = []
        self._conditions[condition].append(self.process_value(name, value))
        return self

    def _merge_condition(
        self, name: str, key: typing.Any, value: typing.Any, negated: bool = False
    ) -> typing.Self:
        """
        Merge new condition with `key` and `value` on given `name`.
        Use this when the given condition maintains key/value pairs
        which is needed to be compressed in one argument,
        `scores={...}` or `advancements={...}` for examples.
        This method internally modifies the state therefore not safe to call.
        """
        condition = (name, negated)
        if negated and not self.AVAILABLE_CONDITIONS[name].negatable:
            raise ValueError('You can\'t negate on condition "%s"' % (name,))

        if condition not in self._conditions:
            self._conditions[condition] = {}
        modify_dict(
            self._conditions[condition],
            {key: self.process_value(name, value)},
            deep=True,
        )
        return self

    def _extend_conditions(
        self, name: str, *values: T, negated: bool = False
    ) -> typing.Self:
        """
        Convenience helper method to add many includes
        or many excludes on given condition `name`.
        """
        copied = deepcopy(self)
        for value in values:
            copied._append_condition(name, value, negated=negated)
        return copied

    def _append_one_include_many_excludes(
        self,
        name: str,
        *excludes: T,
        include: typing.Optional[T] = None,
    ) -> typing.Self:
        """
        Convenience helper method to add at most one include
        and any number of excludes for given condition `name`.
        """
        if include is not None and not excludes:
            raise ValueError(
                "None of `include` and `excludes` are given to condition %s" % (name,)
            )
        copied = deepcopy(self)
        if include is not None:
            copied._append_condition(name, include)
        for exclude in excludes:
            copied._append_condition(name, exclude, negated=True)
        return copied

    # =========================================================================
    # Public condition methods

    def coord(
        self,
        *,
        x: typing.Union[int, float, None] = None,
        y: typing.Union[int, float, None] = None,
        z: typing.Union[int, float, None] = None,
        dx: typing.Union[int, float, None] = None,
        dy: typing.Union[int, float, None] = None,
        dz: typing.Union[int, float, None] = None,
        distance: typing.Union[tuple[float, float], ValueRange, None] = None,
        x_rotation: typing.Union[tuple[float, float], ValueRange, None] = None,
        y_rotation: typing.Union[tuple[float, float], ValueRange, None] = None,
    ) -> typing.Self:
        """
        Add coordinate conditions.
        """
        copied = deepcopy(self)

        if x is not None:
            copied._set_condition("x", x)
        if y is not None:
            copied._set_condition("y", y)
        if z is not None:
            copied._set_condition("z", z)

        assert (dx, dy, dz) == (None, None, None) or None not in (dx, dy, dz)
        if dx is not None:
            copied._set_condition("dx", dx)
        if dy is not None:
            copied._set_condition("dy", dy)
        if dz is not None:
            copied._set_condition("dz", dz)

        assert dx is None or distance is None
        if distance is not None:
            copied._set_condition("distance", distance)

        if x_rotation is not None:
            copied._set_condition("x_rotation", x_rotation)
        if y_rotation is not None:
            copied._set_condition("y_rotation", y_rotation)

        return copied

    def scores(
        self, **scores: typing.Union[ValueRange[int], tuple[int, int], int]
    ) -> typing.Self:
        """
        Add `scores={...}`.
        """
        copied = deepcopy(self)
        for score_name, score_range in scores.items():
            copied._merge_condition("scores", score_name, score_range)
        return copied

    def tags(self, *tags: str, negated: bool = False) -> typing.Self:
        """
        Add `tag=blabla` or `tag=!blabla`, depending on `negated`.
        """
        return self._extend_conditions("tag", *tags, negated=negated)

    def teams(
        self,
        *excludes: typing.Union[str, Team],
        include: typing.Union[str, Team, None] = None,
    ) -> typing.Self:
        """
        Add `team=blabla` or `team=!blabla`.
        """
        return self._append_one_include_many_excludes(
            "team", *excludes, include=include
        )

    def name(self, *excludes: str, include: typing.Optional[str] = None) -> typing.Self:
        """
        Add `name=blabla` or `name=!blabla`.
        """
        return self._append_one_include_many_excludes(
            "name", *excludes, include=include
        )

    def type_(
        self, *excludes: str, include: typing.Optional[str] = None
    ) -> typing.Self:
        """
        Add `type=blabla` or `type=!blabla`.
        """
        return self._append_one_include_many_excludes(
            "type", *excludes, include=include
        )

    def nbt(self, *nbts: typing.Any, negated: bool = False) -> typing.Self:
        """
        Add `nbt={...}` or `nbt=!{...}`, depending on `negated`.
        """
        return self._extend_conditions("nbt", *nbts, negated=negated)

    def level(
        self, level_range: typing.Union[ValueRange[int], tuple[int, int], int]
    ) -> typing.Self:
        """
        Add `level=...`.
        """
        return deepcopy(self)._set_condition("level", level_range)

    def gamemode(
        self,
        *excludes: typing.Union[str, Gamemode],
        include: typing.Union[str, Gamemode, None] = None,
    ) -> typing.Self:
        """
        Add `gamemode=...` or `gamemode=!...`.
        """
        return self._append_one_include_many_excludes(
            "gamemode", *excludes, include=include
        )

    def advancements(
        self, **advancements: typing.Union[bool, dict[str, bool]]
    ) -> typing.Self:
        """
        Add `advancements={...}`.
        `bool` in `advancements` means including only who haven't
        completed the given advancement, not excluding who have completed it.
        """
        copied = deepcopy(self)
        for advancement_name, advancement_value in advancements.items():
            copied._merge_condition("advancements", advancement_name, advancement_value)
        return copied

    def predicate(self, *predicates: str, negated: bool = False) -> typing.Self:
        """
        Add `predicate=blabla` or `predicate=!blabla`, depending on `negate`.
        """
        copied = deepcopy(self)
        for predicate_name in predicates:
            copied._append_condition("predicate", predicate_name, negated=negated)
        return copied

    def limit(self, limit: int) -> typing.Self:
        """
        Add `limit=blabla`.
        """
        assert limit > 0
        return deepcopy(self)._set_condition("limit", limit)

    def sort(self, sorting_mode: SortingMode) -> typing.Self:
        """
        Add `sort=blabla`.
        """
        return deepcopy(self)._set_condition("sort", sorting_mode)
