from pathlib import Path

import pytest
from pydantic import BaseModel, Field

from richforms.api import collect_model
from richforms.config import FormConfig
from tests.helpers import ScriptedInteraction
from tests.models import Manifest


class SimpleModel(BaseModel):
    name: str
    source: str = Field(..., pattern=r"^https?://")
    version: str = "1.0.0"


class InterruptModel(BaseModel):
    name: str
    description: str | None = None


def test_collect_model_supports_default_enter() -> None:
    interaction = ScriptedInteraction(
        responses=[
            "Image",
            "https://example.com/repo",
            "",
        ],
        confirmations=[True],
    )
    config = FormConfig(interaction=interaction)

    model = collect_model(SimpleModel, config=config)

    assert model.name == "Image"
    assert model.source == "https://example.com/repo"
    assert model.version == "1.0.0"


def test_collect_model_reprompts_only_invalid_field_after_validation() -> None:
    interaction = ScriptedInteraction(
        responses=[
            "Image",
            "not-a-url",
            "",
            "https://example.com/repo",
        ],
        confirmations=[True],
    )
    config = FormConfig(interaction=interaction)

    model = collect_model(SimpleModel, config=config)

    assert model.source == "https://example.com/repo"
    prompts = "\n".join(interaction.prompts)
    assert prompts.count("name") == 1
    assert prompts.count("version") == 1
    assert prompts.count("source") == 2


def test_collect_model_list_of_models_collects_nested_fields() -> None:
    interaction = ScriptedInteraction(
        responses=[
            "",
            "Alice",
            "alice@example.com",
            "",
            "",
        ],
        confirmations=[False, True],
    )
    config = FormConfig(interaction=interaction)

    model = collect_model(Manifest, config=config)

    assert model.version == 1
    assert len(model.maintainers) == 1
    assert model.maintainers[0].name == "Alice"
    assert model.maintainers[0].email == "alice@example.com"
    prompts = "\n".join(interaction.prompts)
    assert "maintainers.name" in prompts
    assert "maintainers.email" in prompts


def test_collect_model_interrupt_prompts_to_save_draft_and_reraises(tmp_path: Path) -> None:
    interaction = ScriptedInteraction(
        responses=["Example", "__INTERRUPT__"],
        confirmations=[True],
    )
    config = FormConfig(
        interaction=interaction,
        save_draft_on_interrupt="prompt",
        draft_directory=tmp_path,
    )

    with pytest.raises(KeyboardInterrupt):
        collect_model(InterruptModel, config=config)

    saved = list(tmp_path.glob("interruptmodel-*.yaml"))
    assert len(saved) == 1
    content = saved[0].read_text(encoding="utf-8")
    assert "name: Example" in content


def test_collect_model_interrupt_decline_save_writes_no_file(tmp_path: Path) -> None:
    interaction = ScriptedInteraction(
        responses=["Example", "__INTERRUPT__"],
        confirmations=[False],
    )
    config = FormConfig(
        interaction=interaction,
        save_draft_on_interrupt="prompt",
        draft_directory=tmp_path,
    )

    with pytest.raises(KeyboardInterrupt):
        collect_model(InterruptModel, config=config)

    saved = list(tmp_path.glob("interruptmodel-*.yaml"))
    assert saved == []
