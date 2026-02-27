from __future__ import annotations

import pytest
from rich.console import Console

from richforms.config import RichInteraction
from richforms.prompts import prompt_for_value
from richforms.schema import FieldNode
from tests.helpers import ScriptedInteraction


def _list_node() -> FieldNode:
    return FieldNode(
        path="build.platforms",
        name="platforms",
        title="Platforms",
        description="Target platforms for the build.",
        examples=[],
        required=False,
        annotation=list[str],
        type_label="list[str]",
        has_default=True,
        is_list=True,
        item_annotation=str,
    )


def test_prompt_for_list_with_default_uses_inline_default_instructions() -> None:
    interaction = ScriptedInteraction(responses=[""])
    node = _list_node()

    value = prompt_for_value(
        node=node,
        interaction=interaction,
        console=Console(record=True),
        default_value=["linux/amd64"],
        has_default=True,
        prompt_path="build.platforms",
    )

    assert value == ["linux/amd64"]
    assert interaction.choose_prompts == [
        "build.platforms [bold]Default:[/bold] ['linux/amd64']: "
        "[bold yellow]e[/bold yellow] to edit, [bold red]-[/bold red] to clear, "
        "[bold]↵[/bold] to continue"
    ]


def test_prompt_for_list_with_default_ignores_non_edit_input() -> None:
    interaction = ScriptedInteraction(responses=["x", "not-either", ""])
    node = _list_node()

    value = prompt_for_value(
        node=node,
        interaction=interaction,
        console=Console(record=True),
        default_value=["linux/amd64"],
        has_default=True,
        prompt_path="build.platforms",
    )

    assert value == ["linux/amd64"]
    assert len(interaction.choose_prompts) == 3
    assert len(set(interaction.choose_prompts)) == 1


def test_prompt_for_list_with_default_enters_edit_mode_on_e() -> None:
    interaction = ScriptedInteraction(responses=["e", "linux/arm64", ""])
    node = _list_node()

    value = prompt_for_value(
        node=node,
        interaction=interaction,
        console=Console(record=True),
        default_value=["linux/amd64"],
        has_default=True,
        prompt_path="build.platforms",
    )

    assert value == ["linux/arm64"]
    assert interaction.choose_prompts[0].startswith("build.platforms [bold]Default:[/bold]")
    assert interaction.prompts == [
        "build.platforms[1] (↵ to finish, - to reset)",
        "build.platforms[2] (↵ to finish, - to reset)",
    ]


def test_prompt_for_list_with_default_propagates_keyboard_interrupt() -> None:
    interaction = ScriptedInteraction(responses=["__INTERRUPT__"])
    node = _list_node()

    with pytest.raises(KeyboardInterrupt):
        prompt_for_value(
            node=node,
            interaction=interaction,
            console=Console(record=True),
            default_value=["linux/amd64"],
            has_default=True,
            prompt_path="build.platforms",
        )


def test_rich_interaction_choose_returns_single_keypress(monkeypatch: pytest.MonkeyPatch) -> None:
    console = Console(record=True, force_terminal=True)
    interaction = RichInteraction(console)
    monkeypatch.setattr("richforms.config.click.getchar", lambda: "e")

    assert interaction.choose("Action?", choices={"e", "-"}, default="") == "e"


def test_rich_interaction_choose_returns_default_on_enter(monkeypatch: pytest.MonkeyPatch) -> None:
    console = Console(record=True, force_terminal=True)
    interaction = RichInteraction(console)
    monkeypatch.setattr("richforms.config.click.getchar", lambda: "\n")

    assert interaction.choose("Action?", choices={"e", "-"}, default="") == ""


def test_prompt_for_list_with_default_supports_clear_action() -> None:
    interaction = ScriptedInteraction(responses=["-"])
    node = _list_node()

    value = prompt_for_value(
        node=node,
        interaction=interaction,
        console=Console(record=True),
        default_value=["linux/amd64"],
        has_default=True,
        prompt_path="build.platforms",
    )

    assert value == []


def test_prompt_for_list_item_hint_shows_finish_and_reset() -> None:
    interaction = ScriptedInteraction(responses=["e", "linux/amd64", ""])
    node = _list_node()

    value = prompt_for_value(
        node=node,
        interaction=interaction,
        console=Console(record=True),
        default_value=["linux/amd64"],
        has_default=True,
        prompt_path="build.platforms",
    )

    assert value == ["linux/amd64"]
    assert interaction.prompts == [
        "build.platforms[1] (↵ to finish, - to reset)",
        "build.platforms[2] (↵ to finish, - to reset)",
    ]


def test_prompt_for_list_dash_resets_current_edit_session() -> None:
    interaction = ScriptedInteraction(responses=["e", "linux/arm64", "-", "linux/amd64", ""])
    node = _list_node()

    value = prompt_for_value(
        node=node,
        interaction=interaction,
        console=Console(record=True),
        default_value=["linux/amd64"],
        has_default=True,
        prompt_path="build.platforms",
    )

    assert value == ["linux/amd64"]
    assert interaction.prompts == [
        "build.platforms[1] (↵ to finish, - to reset)",
        "build.platforms[2] (↵ to finish, - to reset)",
        "build.platforms[1] (↵ to finish, - to reset)",
        "build.platforms[2] (↵ to finish, - to reset)",
    ]


def test_prompt_for_optional_with_default_supports_clear_token() -> None:
    node = FieldNode(
        path="notes",
        name="notes",
        title="Notes",
        description="Optional notes.",
        examples=[],
        required=False,
        annotation=str,
        type_label="str",
        has_default=True,
    )
    interaction = ScriptedInteraction(responses=["-"])

    value = prompt_for_value(
        node=node,
        interaction=interaction,
        console=Console(record=True),
        default_value="keep-me",
        has_default=True,
        prompt_path="notes",
    )

    assert value is None
