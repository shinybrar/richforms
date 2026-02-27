from __future__ import annotations

import importlib
from pathlib import Path
from typing import Annotated, Any, Literal

import typer
from pydantic import BaseModel, ValidationError

from richforms.api import edit as edit_form
from richforms.api import fill as fill_form
from richforms.config import FormConfig
from richforms.exceptions import ExcludedFieldResolutionError
from richforms.io import load_payload_file
from richforms.serializers import serialize_result

app = typer.Typer(help="Rich terminal forms powered by Pydantic models.")
OutputFormat = Literal["json", "yaml"]


@app.command(help="Create a new form.")
def fill(
    model: Annotated[str, typer.Argument(help="Model path as module:ModelName")],
    from_file: Annotated[
        Path | None,
        typer.Option("--from-file", help="Optional initial JSON/YAML file", exists=True),
    ] = None,
    output: Annotated[Path | None, typer.Option("--output", help="Output file path")] = None,
    format: Annotated[
        OutputFormat | None,
        typer.Option(help="Output format (defaults to output extension when provided)"),
    ] = None,
    clear: Annotated[
        bool,
        typer.Option("--clear/--no-clear", help="Clear the terminal between each field"),
    ] = True,
) -> None:
    model_type = _load_model_type(model)
    try:
        initial = load_payload_file(from_file) if from_file else None
    except ValueError as exc:
        raise typer.BadParameter(str(exc), param_hint="--from-file") from exc
    config = FormConfig(clear_on_step=clear)
    try:
        result = fill_form(model_type, initial=initial, config=config)
    except ExcludedFieldResolutionError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(code=2) from exc
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
    format: Annotated[
        OutputFormat | None,
        typer.Option(help="Output format (defaults to output extension when provided)"),
    ] = None,
    clear: Annotated[
        bool,
        typer.Option("--clear/--no-clear", help="Clear the terminal between each field"),
    ] = True,
) -> None:
    model_type = _load_model_type(model)
    try:
        payload = load_payload_file(from_file)
    except ValueError as exc:
        raise typer.BadParameter(str(exc), param_hint="--from-file") from exc
    try:
        instance = model_type.model_validate(payload)
    except ValidationError as exc:
        details = _validation_error_summary(exc)
        raise typer.BadParameter(
            f"Input payload does not match {model_type.__name__}: {details}",
            param_hint="--from-file",
        ) from exc
    config = FormConfig(clear_on_step=clear)
    try:
        result = edit_form(instance, config=config)
    except ExcludedFieldResolutionError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(code=2) from exc
    except KeyboardInterrupt as exc:
        typer.echo("Form entry interrupted.", err=True)
        raise typer.Exit(code=130) from exc
    _emit_result(result=result, output=output, format=format)


def main() -> None:
    app()


def _emit_result(
    *, result: BaseModel, output: Path | None, format: OutputFormat | None
) -> None:
    resolved_format = _resolve_output_format(output=output, format=format)
    if (
        output is not None
        and format is not None
        and (inferred := _infer_format_from_path(output)) is not None
        and inferred != format
    ):
        typer.echo(
            f"Warning: --format {format} does not match output extension '{output.suffix}'. "
            f"Writing {format}.",
            err=True,
        )
    payload = serialize_result(result, format=resolved_format, path=output)
    if output:
        typer.echo(f"Wrote {resolved_format} output to {output}")
        return
    typer.echo(payload or "")


def _load_model_type(model_path: str) -> type[BaseModel]:
    if ":" not in model_path:
        raise typer.BadParameter("Model must use module:ModelName format")
    module_name, _, class_name = model_path.partition(":")
    try:
        module = importlib.import_module(module_name)
    except ModuleNotFoundError as exc:
        if exc.name == module_name or (
            exc.name is not None and exc.name.startswith(module_name + ".")
        ):
            raise typer.BadParameter(f"Could not import module '{module_name}'") from exc
        dependency = exc.name or "unknown dependency"
        raise typer.BadParameter(
            f"Could not import module '{module_name}' because dependency '{dependency}' is missing"
        ) from exc
    except Exception as exc:
        raise typer.BadParameter(f"Could not import module '{module_name}': {exc}") from exc
    model_type: Any = getattr(module, class_name, None)
    if model_type is None:
        raise typer.BadParameter(f"Model class not found: {class_name}")
    if not isinstance(model_type, type) or not issubclass(model_type, BaseModel):
        raise typer.BadParameter(f"{class_name} is not a Pydantic BaseModel")
    return model_type


def _resolve_output_format(*, output: Path | None, format: OutputFormat | None) -> OutputFormat:
    if format is not None:
        return format
    inferred = _infer_format_from_path(output) if output is not None else None
    return inferred or "json"


def _infer_format_from_path(path: Path) -> OutputFormat | None:
    suffix = path.suffix.lower()
    if suffix in {".yaml", ".yml"}:
        return "yaml"
    if suffix == ".json":
        return "json"
    return None


def _validation_error_summary(exc: ValidationError) -> str:
    first = exc.errors()[0]
    location = ".".join(str(part) for part in first.get("loc", ()) if part is not None)
    message = str(first.get("msg", "Invalid value"))
    if location:
        return f"{location}: {message}"
    return message
