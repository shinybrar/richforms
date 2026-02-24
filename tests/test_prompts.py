from __future__ import annotations

import pytest
from rich.console import Console

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
    assert interaction.prompts == [
        "build.platforms [bold]Default:[/bold] ['linux/amd64']: "
        "[bold yellow]e[/bold yellow] to edit, [bold]↵[/bold] to continue"
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
    assert len(interaction.prompts) == 3
    assert len(set(interaction.prompts)) == 1


def test_prompt_for_list_with_default_enters_edit_mode_on_e() -> None:
    interaction = ScriptedInteraction(responses=["e", "linux/arm64"])
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
    assert interaction.prompts[0].startswith("build.platforms [bold]Default:[/bold]")
    assert interaction.prompts[1] == "build.platforms[1]"


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
