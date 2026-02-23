from __future__ import annotations

import warnings
from collections.abc import Iterable
from typing import Any, TypeVar, cast

from pydantic import BaseModel
from rich.console import Console

from richforms.config import FormConfig, Interaction, RichInteraction
from richforms.drafts import build_draft_path, save_draft_yaml
from richforms.exceptions import ExcludedFieldResolutionError
from richforms.introspection import build_model_schema
from richforms.prompts import prompt_for_value
from richforms.render import (
    render_editor_view,
    render_review,
    render_validation_ledger,
)
from richforms.schema import FieldNode, ModelSchema
from richforms.serializers import Format, serialize_result
from richforms.state import (
    copy_initial,
    get_nested_value,
    has_nested_value,
    set_nested_value,
)
from richforms.validate import validate_draft

T = TypeVar("T", bound=BaseModel)


def fill(
    model_type: type[T],
    *,
    initial: dict[str, Any] | None = None,
    config: FormConfig | None = None,
    console: Console | None = None,
    _path_prefix: str = "",
    _handle_interrupt: bool = True,
) -> T:
    cfg = config or FormConfig()
    resolved_console = console or cfg.console or Console()
    interaction: Interaction = cfg.interaction or RichInteraction(resolved_console)
    schema = build_model_schema(model_type)
    draft = copy_initial(initial)
    first_pass = True
    errors: dict[str, str] = {}

    try:
        while True:
            targets = _target_nodes(schema, errors=errors, first_pass=first_pass)
            for index, node in enumerate(targets, start=1):
                current_value, has_default = _resolve_default(node=node, draft=draft)
                display_path = _display_path(node.path, _path_prefix)
                if cfg.clear_on_step and resolved_console.is_terminal:
                    resolved_console.clear()
                cockpit = render_editor_view(
                    nodes=schema.leaf_nodes,
                    node=node,
                    index=index,
                    total=len(targets),
                    current_path=display_path,
                    error=errors.get(node.path),
                    has_default=has_default,
                    default_value=current_value,
                    path_prefix=_path_prefix,
                    completed_paths=set(
                        _prefixed_paths(_completed_paths(schema, draft), _path_prefix)
                    ),
                    error_paths=set(_prefixed_paths(errors.keys(), _path_prefix)),
                    console_width=resolved_console.width,
                )
                resolved_console.print(cockpit)
                value = prompt_for_value(
                    node=node,
                    interaction=interaction,
                    console=resolved_console,
                    default_value=current_value,
                    has_default=has_default,
                    prompt_path=display_path,
                )
                resolved_console.print()
                set_nested_value(draft, node.path, value)

            result = validate_draft(model_type, draft)
            if result.model is not None:
                resolved_console.print(render_review(result.model))
                if cfg.confirm_before_return and not interaction.confirm(
                    "Accept this form submission?", default=True
                ):
                    path = interaction.ask(
                        "Enter a field path to edit (blank to keep current values):",
                        default="",
                    )
                    errors = {path: "Manual edit requested"} if path else {}
                    first_pass = False
                    continue
                return cast(T, result.model)

            excluded_errors = _excluded_errors(result.errors, schema)
            if excluded_errors:
                raise ExcludedFieldResolutionError(excluded_errors)

            errors = _normalize_errors(result.errors, schema)
            resolved_console.print(
                render_validation_ledger(_prefixed_error_map(errors, _path_prefix))
            )
            first_pass = False
    except KeyboardInterrupt:
        if _handle_interrupt:
            _handle_keyboard_interrupt(
                cfg=cfg,
                interaction=interaction,
                console=resolved_console,
                model_type=model_type,
                draft=draft,
            )
        raise


def edit_model(
    instance: T,
    *,
    config: FormConfig | None = None,
    console: Console | None = None,
) -> T:
    warnings.warn(
        "richforms.api.edit_model is deprecated; use richforms.api.edit instead",
        DeprecationWarning,
        stacklevel=2,
    )
    return edit(instance, config=config, console=console)


def edit(
    instance: T,
    *,
    config: FormConfig | None = None,
    console: Console | None = None,
) -> T:
    return fill(
        type(instance),
        initial=instance.model_dump(mode="python"),
        config=config,
        console=console,
    )


def collect_model(
    model_type: type[T],
    *,
    initial: dict[str, Any] | None = None,
    config: FormConfig | None = None,
    console: Console | None = None,
    _path_prefix: str = "",
    _handle_interrupt: bool = True,
) -> T:
    warnings.warn(
        "richforms.api.collect_model is deprecated; use richforms.api.fill instead",
        DeprecationWarning,
        stacklevel=2,
    )
    return fill(
        model_type,
        initial=initial,
        config=config,
        console=console,
        _path_prefix=_path_prefix,
        _handle_interrupt=_handle_interrupt,
    )


def collect_dict(
    model_type: type[T],
    *,
    initial: dict[str, Any] | None = None,
    config: FormConfig | None = None,
    console: Console | None = None,
) -> dict[str, Any]:
    model = fill(model_type, initial=initial, config=config, console=console)
    return model.model_dump(mode="python")


def serialize_model_result(
    model: BaseModel, *, format: Format, path: str | None = None
) -> str | None:
    from pathlib import Path

    out_path = Path(path) if path else None
    return serialize_result(model, format=format, path=out_path)


def _target_nodes(
    schema: ModelSchema, *, errors: dict[str, str], first_pass: bool
) -> list[FieldNode]:
    if first_pass:
        return schema.leaf_nodes
    return [node for node in schema.leaf_nodes if node.path in errors]


def _resolve_default(*, node: FieldNode, draft: dict[str, Any]) -> tuple[Any, bool]:
    if has_nested_value(draft, node.path):
        return get_nested_value(draft, node.path), True
    if node.has_default:
        return node.default, True
    return None, False


def _normalize_errors(errors: dict[str, str], schema: ModelSchema) -> dict[str, str]:
    if not errors:
        return {}
    normalized: dict[str, str] = {}
    known_paths = schema.by_path
    for path, message in errors.items():
        if path in known_paths:
            normalized[path] = message
            continue
        for known in known_paths:
            if known.startswith(path + "."):
                normalized[known] = message
                break
    return normalized


def _excluded_errors(errors: dict[str, str], schema: ModelSchema) -> dict[str, str]:
    if not errors or not schema.excluded_paths:
        return {}
    return {
        path: message
        for path, message in errors.items()
        if _matches_excluded_path(path, schema.excluded_paths)
    }


def _matches_excluded_path(path: str, excluded_paths: set[str]) -> bool:
    if path in excluded_paths:
        return True
    return any(excluded.startswith(path + ".") for excluded in excluded_paths)


def _completed_paths(schema: ModelSchema, draft: dict[str, Any]) -> list[str]:
    return [node.path for node in schema.leaf_nodes if has_nested_value(draft, node.path)]


def _display_path(path: str, prefix: str) -> str:
    if not prefix:
        return path
    return f"{prefix}.{path}"


def _prefixed_paths(paths: Iterable[str], prefix: str) -> list[str]:
    return [_display_path(path, prefix) for path in paths]


def _prefixed_error_map(errors: dict[str, str], prefix: str) -> dict[str, str]:
    return {_display_path(path, prefix): message for path, message in errors.items()}


def _handle_keyboard_interrupt(
    *,
    cfg: FormConfig,
    interaction: Interaction,
    console: Console,
    model_type: type[BaseModel],
    draft: dict[str, Any],
) -> None:
    style = cfg.interrupt_message_style
    if not draft:
        console.print("Form entry interrupted.", style=style)
        return

    save_mode = cfg.save_draft_on_interrupt
    save_path = build_draft_path(model_type.__name__, directory=cfg.draft_directory)
    should_save = False
    if save_mode == "always":
        should_save = True
    elif save_mode == "prompt":
        should_save = interaction.confirm(f"Save draft to {save_path}?", default=True)

    if not should_save:
        console.print("Form entry interrupted. Draft not saved.", style=style)
        return

    try:
        save_draft_yaml(draft, path=save_path)
    except Exception as exc:  # pragma: no cover
        console.print(f"Form entry interrupted. Failed to save draft: {exc}", style="bold red")
        return

    console.print(
        f"Draft saved to {save_path}. Restart with --from-file {save_path}",
        style=style,
    )
