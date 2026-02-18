from pathlib import Path

from rich.prompt import Confirm, Prompt
from typer.testing import CliRunner

from richforms.cli import app

runner = CliRunner()


def test_fill_command_writes_output_file(tmp_path: Path) -> None:
    from_file = tmp_path / "input.json"
    from_file.write_text('{"name":"Example","source":"https://example.com/repo"}', encoding="utf-8")
    out_file = tmp_path / "output.json"

    result = runner.invoke(
        app,
        [
            "fill",
            "tests.cli_models:CliModel",
            "--from-file",
            str(from_file),
            "--output",
            str(out_file),
        ],
        input="\n\n\ny\n",
    )

    assert result.exit_code == 0
    assert out_file.exists()
    assert '"name": "Example"' in out_file.read_text(encoding="utf-8")


def test_edit_command_writes_output_file(tmp_path: Path) -> None:
    from_file = tmp_path / "input.json"
    from_file.write_text('{"name":"Old","source":"https://example.com/repo"}', encoding="utf-8")
    out_file = tmp_path / "output.json"

    result = runner.invoke(
        app,
        [
            "edit",
            "tests.cli_models:CliModel",
            "--from-file",
            str(from_file),
            "--output",
            str(out_file),
        ],
        input="New Name\n\ny\n",
    )

    assert result.exit_code == 0
    assert '"name": "New Name"' in out_file.read_text(encoding="utf-8")


def test_fill_interrupt_shows_resume_hint_and_exits(tmp_path: Path, monkeypatch) -> None:
    state = {"calls": 0}

    def fake_ask(prompt: str, default: str | None = None, console=None) -> str:
        del prompt, default, console
        state["calls"] += 1
        if state["calls"] == 1:
            return "Example"
        raise KeyboardInterrupt

    def fake_confirm(prompt: str, default: bool = True, console=None) -> bool:
        del prompt, default, console
        return True

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(Prompt, "ask", fake_ask)
    monkeypatch.setattr(Confirm, "ask", fake_confirm)

    result = runner.invoke(app, ["fill", "tests.cli_models:CliModel"])

    assert result.exit_code == 130
    assert "--from-file" in result.output
    assert ".richforms-drafts" in result.output
