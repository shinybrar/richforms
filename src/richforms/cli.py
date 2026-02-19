from __future__ import annotations

import importlib
from pathlib import Path
from typing import Annotated, Any, Literal

import typer
from pydantic import BaseModel

from richforms.api import edit as edit_form
from richforms.api import fill as fill_form
from richforms.config import FormConfig
from richforms.io import load_payload_file
from richforms.serializers import serialize_result

app = typer.Typer(help="Rich terminal forms powered by Pydantic models.")
OutputFormat = Literal["json", "yaml"]


@app.command(help="Create a new form.")
def fill(
    model: Annotated[str, typer.Argument(help="Model path as module:ModelName")],
    from_file: Annotated[
        Path | None, typer.Option("--from-file", help="Optional initial JSON/YAML file")
    ] = None,
    output: Annotated[Path | None, typer.Option("--output", help="Output file path")] = None,
    format: Annotated[OutputFormat, typer.Option("--format", help="Output format")] = "json",
    clear: Annotated[
        bool,
        typer.Option("--clear/--no-clear", help="Clear the terminal between each field"),
    ] = True,
) -> None:
    model_type = _load_model_type(model)
    initial = load_payload_file(from_file) if from_file else None
    config = FormConfig(clear_on_step=clear)
    try:
        result = fill_form(model_type, initial=initial, config=config)
    except KeyboardInterrupt as exc:
        typer.echo("Form entry interrupted.", err=True)
        raise typer.Exit(code=130) from exc
    _emit_result(result=result, output=output, format=format)


@app.command(help="Edit a saved form.")
def edit(
    model: Annotated[str, typer.Argument(help="Model path as module:ModelName")],
    from_file: Annotated[
        Path, typer.Option("--from-file", help="Input JSON/YAML file", exists=True)
    ],
    output: Annotated[Path | None, typer.Option("--output", help="Output file path")] = None,
    format: Annotated[OutputFormat, typer.Option("--format", help="Output format")] = "json",
    clear: Annotated[
        bool,
        typer.Option("--clear/--no-clear", help="Clear the terminal between each field"),
    ] = True,
) -> None:
    model_type = _load_model_type(model)
    payload = load_payload_file(from_file)
    instance = model_type.model_validate(payload)
    config = FormConfig(clear_on_step=clear)
    try:
        result = edit_form(instance, config=config)
    except KeyboardInterrupt as exc:
        typer.echo("Form entry interrupted.", err=True)
        raise typer.Exit(code=130) from exc
    _emit_result(result=result, output=output, format=format)


def main() -> None:
    app()


def _emit_result(*, result: BaseModel, output: Path | None, format: OutputFormat) -> None:
    payload = serialize_result(result, format=format, path=output)
    if output:
        typer.echo(f"Wrote {format} output to {output}")
        return
    typer.echo(payload or "")


def _load_model_type(model_path: str) -> type[BaseModel]:
    if ":" not in model_path:
        raise typer.BadParameter("Model must use module:ModelName format")
    module_name, _, class_name = model_path.partition(":")
    module = importlib.import_module(module_name)
    model_type: Any = getattr(module, class_name, None)
    if model_type is None:
        raise typer.BadParameter(f"Model class not found: {class_name}")
    if not isinstance(model_type, type) or not issubclass(model_type, BaseModel):
        raise typer.BadParameter(f"{class_name} is not a Pydantic BaseModel")
    return model_type
