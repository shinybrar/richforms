import warnings
from pathlib import Path

import pytest
from pydantic import BaseModel, Field
from rich.console import Console

from richforms import edit, fill
from richforms.api import collect_model, edit_model
from richforms.config import FormConfig
from richforms.exceptions import ExcludedFieldResolutionError
from tests.helpers import ScriptedInteraction
from tests.models import Manifest


class SimpleModel(BaseModel):
    name: str
    source: str = Field(..., pattern=r"^https?://")
    version: str = "1.0.0"


class InterruptModel(BaseModel):
    name: str
    description: str | None = None


class OptionalDefaultModel(BaseModel):
    note: str | None = "keep-me"


class OptionalListModel(BaseModel):
    tags: list[str] = Field(default_factory=list)


class ItemModel(BaseModel):
    name: str


class ModelListEditModel(BaseModel):
    items: list[ItemModel] = Field(default_factory=list)


class ExcludedLeafPromptModel(BaseModel):
    name: str
    revision: int = Field(0, json_schema_extra={"richforms": {"exclude": True}})


class ExcludedRequiredModel(BaseModel):
    system_id: str = Field(..., json_schema_extra={"richforms": {"exclude": True}})


class ExcludedRequiredWithInitialModel(BaseModel):
    name: str
    system_id: str = Field(..., json_schema_extra={"richforms": {"exclude": True}})


class ExcludedWithDefaultFactoryModel(BaseModel):
    name: str
    created_at: str = Field(
        default_factory=lambda: "2026-02-23T00:00:00Z",
        json_schema_extra={"richforms": {"exclude": True}},
    )


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

    model = fill(SimpleModel, config=config)

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

    model = fill(SimpleModel, config=config)

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

    model = fill(Manifest, config=config)

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
        fill(InterruptModel, config=config)

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
        fill(InterruptModel, config=config)

    saved = list(tmp_path.glob("interruptmodel-*.yaml"))
    assert saved == []


def test_edit_updates_existing_model_values() -> None:
    interaction = ScriptedInteraction(responses=["New Name", "", ""], confirmations=[True])
    config = FormConfig(interaction=interaction)
    instance = SimpleModel(name="Old Name", source="https://example.com/repo")

    model = edit(instance, config=config)

    assert model.name == "New Name"
    assert model.source == "https://example.com/repo"


def test_edit_allows_clearing_optional_prefilled_value() -> None:
    interaction = ScriptedInteraction(responses=["-"], confirmations=[True])
    config = FormConfig(interaction=interaction)
    instance = OptionalDefaultModel(note="existing")

    model = edit(instance, config=config)

    assert model.note is None


def test_edit_list_default_edit_mode_allows_blank_to_clear_list() -> None:
    interaction = ScriptedInteraction(responses=["e", ""], confirmations=[True])
    config = FormConfig(interaction=interaction)
    instance = OptionalListModel(tags=["linux/amd64"])

    model = edit(instance, config=config)

    assert model.tags == []


def test_edit_model_list_can_replace_existing_with_empty_list() -> None:
    interaction = ScriptedInteraction(responses=["e"], confirmations=[False, True])
    config = FormConfig(interaction=interaction)
    instance = ModelListEditModel(items=[ItemModel(name="Alice")])

    model = edit(instance, config=config)

    assert model.items == []


def test_fill_reprompts_when_manual_edit_path_is_invalid() -> None:
    interaction = ScriptedInteraction(
        responses=[
            "Image",
            "https://example.com/repo",
            "",
            "sorce",
            "source",
            "https://example.com/new-repo",
        ],
        confirmations=[False, True],
    )
    console = Console(record=True)
    config = FormConfig(interaction=interaction, console=console, clear_on_step=False)

    model = fill(SimpleModel, config=config)

    assert model.source == "https://example.com/new-repo"
    prompt = "Enter a field path to edit (blank to keep current values):"
    assert interaction.prompts.count(prompt) == 2
    assert "Did you mean: source?" in console.export_text()


def test_collect_model_alias_emits_deprecation_warning() -> None:
    interaction = ScriptedInteraction(
        responses=[
            "Image",
            "https://example.com/repo",
            "",
        ],
        confirmations=[True],
    )
    config = FormConfig(interaction=interaction)

    with warnings.catch_warnings(record=True) as records:
        warnings.simplefilter("always", DeprecationWarning)
        model = collect_model(SimpleModel, config=config)

    assert model.name == "Image"
    assert any(item.category is DeprecationWarning for item in records)


def test_edit_model_alias_emits_deprecation_warning() -> None:
    interaction = ScriptedInteraction(responses=["Updated", "", ""], confirmations=[True])
    config = FormConfig(interaction=interaction)
    instance = SimpleModel(name="Old Name", source="https://example.com/repo")

    with warnings.catch_warnings(record=True) as records:
        warnings.simplefilter("always", DeprecationWarning)
        model = edit_model(instance, config=config)

    assert model.name == "Updated"
    assert any(item.category is DeprecationWarning for item in records)


def test_fill_does_not_prompt_fields_marked_excluded() -> None:
    interaction = ScriptedInteraction(responses=["Image"], confirmations=[True])
    config = FormConfig(interaction=interaction)

    model = fill(ExcludedLeafPromptModel, config=config)

    assert model.name == "Image"
    assert model.revision == 0
    prompts = "\n".join(interaction.prompts)
    assert "name" in prompts
    assert "revision" not in prompts


def test_fill_raises_clear_error_for_unresolved_excluded_required_field() -> None:
    interaction = ScriptedInteraction(responses=[], confirmations=[])
    config = FormConfig(interaction=interaction)

    with pytest.raises(ExcludedFieldResolutionError, match="system_id"):
        fill(ExcludedRequiredModel, config=config)


def test_fill_allows_excluded_required_field_with_initial_value() -> None:
    interaction = ScriptedInteraction(responses=["Widget"], confirmations=[True])
    config = FormConfig(interaction=interaction)

    model = fill(
        ExcludedRequiredWithInitialModel,
        initial={"system_id": "sys-1234"},
        config=config,
    )

    assert model.name == "Widget"
    assert model.system_id == "sys-1234"
    prompts = "\n".join(interaction.prompts)
    assert "system_id" not in prompts


def test_fill_allows_excluded_field_with_default_factory() -> None:
    interaction = ScriptedInteraction(responses=["Widget"], confirmations=[True])
    config = FormConfig(interaction=interaction)

    model = fill(ExcludedWithDefaultFactoryModel, config=config)

    assert model.name == "Widget"
    assert model.created_at == "2026-02-23T00:00:00Z"
    prompts = "\n".join(interaction.prompts)
    assert "created_at" not in prompts
