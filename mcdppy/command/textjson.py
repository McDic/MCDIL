"""
Provides NBT classes for raw JSON text format.
"""

import re
import typing
from copy import deepcopy

from .nbt import NBT

if typing.TYPE_CHECKING:
    from . import *


class TextJson(NBT):
    """
    Common class of all `TextJson` components.
    You can directly instantiate stuffs using this class,
    but use utility classes whenever it is possible.
    """

    COLOR_HEX_SYNTAX: typing.Final[re.Pattern] = re.compile("^#[0-9A-F]{6}$")
    DEFAULT_COLORS: typing.Final[set[str]] = {
        "black",
        "dark_blue",
        "dark_green",
        "dark_aqua",
        "dark_red",
        "dark_purple",
        "gold",
        "gray",
        "dark_gray",
        "blue",
        "green",
        "aqua",
        "red",
        "light_purple",
        "yellow",
        "white",
    }

    class HoverEventShowItem(typing.TypedDict):
        id: str
        count: typing.NotRequired[int]
        tag: typing.NotRequired["NBT"]

    class HoverEventShowEntity(typing.TypedDict):
        type: str
        id: list[int]
        name: typing.NotRequired[str]

    @staticmethod
    def set_if_present(data: dict[str, typing.Any], key: str, value: typing.Any):
        """
        Convenient method for doing `if value is not None: data[key] = value`.
        """
        if value is not None:
            data[key] = value

    def __init__(
        self,
        *extra: typing.Self,
        content: typing.Optional[dict[str, typing.Any]] = None,
        color: typing.Optional[str] = None,
        font: typing.Optional[str] = None,
        bold: typing.Optional[bool] = None,
        italic: typing.Optional[bool] = None,
        underlined: typing.Optional[bool] = None,
        strikethrough: typing.Optional[bool] = None,
        obfuscated: typing.Optional[bool] = None,
        insertion: typing.Optional[str] = None,
        click_event: typing.Optional[
            tuple[
                typing.Literal[
                    "open_url",
                    "open_file",
                    "run_command",
                    "suggest_command",
                    "change_page",
                    "copy_to_clipboard",
                ],
                str,
            ]
        ] = None,
        hover_event: typing.Union[
            tuple[typing.Literal["show_text"], "TextJson"],
            tuple[typing.Literal["show_item"], HoverEventShowItem],
            tuple[typing.Literal["show_entity"], HoverEventShowEntity],
            None,
        ] = None,
        **kwargs,
    ):
        data: dict[str, typing.Any] = deepcopy(content or {"text": ""})
        assert (
            color is None
            or self.COLOR_HEX_SYNTAX.fullmatch(color)
            or color in self.DEFAULT_COLORS
        )

        # Extra components
        if extra:
            self.set_if_present(data, "extra", list(extra))

        # Base options
        self.set_if_present(data, "color", color)
        self.set_if_present(data, "font", font)
        self.set_if_present(data, "bold", bold)
        self.set_if_present(data, "italic", italic)
        self.set_if_present(data, "underlined", underlined)
        self.set_if_present(data, "strikethrough", strikethrough)
        self.set_if_present(data, "obfuscated", obfuscated)

        # Interactions
        self.set_if_present(data, "insertion", insertion)
        if click_event:
            action, command = click_event
            command = str(command)
            if not command.startswith("/"):
                command = "/" + command
            self.set_if_present(
                data, "clickEvent", {"action": action, "value": command}
            )
        if hover_event:
            self.set_if_present(
                data,
                "hoverEvent",
                {"action": hover_event[0], "contents": hover_event[1]},
            )

        # Go NBT initialization
        super().__init__(data, **kwargs)


class TextJsonPlain(TextJson):
    """
    Represents plain text as one of components in `TextJson`.
    """

    def __init__(self, text: str, **kwargs):
        super().__init__(content={"text": text}, **kwargs)


class TextJsonScoreboardValue(TextJson):
    """
    Represents scoreboard value as one of components in `TextJson`.
    """

    def __init__(
        self,
        name: typing.Union[str, "TargetSelector"],
        objective: typing.Union[str, "ScoreboardObjective"],
        **kwargs,
    ):
        super().__init__(
            content={"score": {"name": str(name), "objective": str(objective)}},
            **kwargs,
        )


class TextJsonEntityName(TextJson):
    """
    Represents entity name as one of components in `TextJson`.
    """

    def __init__(
        self,
        selector: typing.Union[str, "TargetSelector"],
        separator: typing.Union[str, TextJson, None] = None,
        **kwargs,
    ):
        data = {"selector": str(selector)}
        self.set_if_present(data, "separator", separator)
        super().__init__(content=data, **kwargs)


class TextJsonKeybind(TextJson):
    """
    Represents entity name as one of components in `TextJson`.
    """

    def __init__(self, keybind: str, **kwargs):
        super().__init__(content={"keybind": keybind}, **kwargs)


class TextJsonNBT(TextJson):
    """
    Represents entity name as one of components in `TextJson`.
    """

    def __init__(
        self,
        nbt_path: str,
        interpret: bool = False,
        separator: typing.Optional[TextJson] = None,
        block: typing.Optional[str] = None,
        **kwargs,
    ):
        data = {"nbt_path": nbt_path, "interpret": interpret}
        self.set_if_present(data, "separator", separator)
        super().__init__(content=data, **kwargs)
