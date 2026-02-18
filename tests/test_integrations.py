from pathlib import Path

from richforms.config import FormConfig
from richforms.integrations.click import form_callback as click_form_callback
from richforms.integrations.typer import form_callback as typer_form_callback
from tests.cli_models import CliModel
from tests.helpers import ScriptedInteraction


def test_click_form_callback_collects_interactively_when_value_missing() -> None:
    interaction = ScriptedInteraction(
        responses=["Example", "https://example.com/repo"], confirmations=[True]
    )
    callback = click_form_callback(CliModel, config=FormConfig(interaction=interaction))

    model = callback(None, None, None)

    assert model.name == "Example"
    assert str(model.source) == "https://example.com/repo"


def test_click_form_callback_loads_file_when_value_provided(tmp_path: Path) -> None:
    payload = tmp_path / "payload.json"
    payload.write_text('{"name":"FromFile","source":"https://example.com/repo"}', encoding="utf-8")
    callback = click_form_callback(CliModel)

    model = callback(None, None, payload)

    assert model.name == "FromFile"


def test_typer_form_callback_loads_file(tmp_path: Path) -> None:
    payload = tmp_path / "payload.json"
    payload.write_text('{"name":"FromFile","source":"https://example.com/repo"}', encoding="utf-8")
    callback = typer_form_callback(CliModel)

    model = callback(payload)

    assert model.name == "FromFile"
