from __future__ import annotations

import inspect
from typing import Any

from pydantic import BaseModel, TypeAdapter, ValidationError
from rich.console import Console

from richforms.config import FormConfig, Interaction
from richforms.schema import FieldNode


def prompt_for_value(
    *,
    node: FieldNode,
    interaction: Interaction,
    console: Console,
    default_value: Any,
    has_default: bool,
    prompt_path: str,
) -> Any:
    optional_hint = "Press Enter to continue without a value."
    if node.is_list:
        return _prompt_for_list(
            node=node,
            interaction=interaction,
            console=console,
            default_value=default_value,
            has_default=has_default,
            prompt_path=prompt_path,
        )

    while True:
        default_text = _default_to_text(default_value) if has_default else None
        prompt = prompt_path
        if not node.required:
            prompt = f"{prompt_path} ({optional_hint})"
        raw = interaction.ask(prompt, default=default_text)
        if raw == "" and has_default:
            return default_value
        if raw == "" and not node.required:
            return None
        try:
            return _parse_value(node=node, raw=raw)
        except (ValidationError, ValueError) as exc:
            message = exc.errors()[0]["msg"] if isinstance(exc, ValidationError) else str(exc)
            console.print(f"[red]Invalid value for {prompt_path}: {message}[/red]")


def _prompt_for_list(
    *,
    node: FieldNode,
    interaction: Interaction,
    console: Console,
    default_value: Any,
    has_default: bool,
    prompt_path: str,
) -> list[Any]:
    optional_hint = "Press Enter to continue without a value."
    item_annotation = node.item_annotation or str
    item_model = _as_model(item_annotation)
    if item_model is not None:
        return _prompt_for_model_list(
            node=node,
            interaction=interaction,
            console=console,
            default_value=default_value,
            has_default=has_default,
            prompt_path=prompt_path,
            item_model=item_model,
        )

    if has_default:
        decision = interaction.ask(f"{prompt_path} (type 'edit' to change list)", default="")
        if decision == "":
            return list(default_value)

    item_adapter = TypeAdapter(item_annotation)
    values: list[Any] = []
    index = 1
    while True:
        prompt = f"{prompt_path}[{index}]"
        if not node.required and not has_default and index == 1:
            prompt = f"{prompt} ({optional_hint})"
        raw = interaction.ask(prompt)
        if raw == "" and not node.required and not has_default and index == 1:
            return []
        try:
            values.append(item_adapter.validate_python(raw))
        except ValidationError as exc:
            console.print(f"[red]Invalid value for {prompt_path}: {exc.errors()[0]['msg']}[/red]")
            continue
        if not interaction.confirm(f"Add another item for {prompt_path}?", default=False):
            break
        index += 1
    return values


def _prompt_for_model_list(
    *,
    node: FieldNode,
    interaction: Interaction,
    console: Console,
    default_value: Any,
    has_default: bool,
    prompt_path: str,
    item_model: type[BaseModel],
) -> list[Any]:
    existing = list(default_value) if has_default and isinstance(default_value, list) else []
    if existing and interaction.confirm(f"Use existing values for {prompt_path}?", default=True):
        return existing

    values: list[Any] = []
    collect_first = bool(node.required and not existing)
    item_number = 1
    while True:
        if not collect_first and not interaction.confirm(
            f"Add item to {prompt_path}?", default=False
        ):
            break
        collect_first = False
        console.print(f"[cyan]Collecting {prompt_path} item #{item_number}[/cyan]")
        from richforms.api import collect_model

        child_config = FormConfig(
            interaction=interaction,
            console=console,
            confirm_before_return=False,
        )
        item = collect_model(
            item_model,
            config=child_config,
            console=console,
            _path_prefix=prompt_path,
            _handle_interrupt=False,
        )
        values.append(item.model_dump(mode="python"))
        if not interaction.confirm(f"Add another item for {prompt_path}?", default=False):
            break
        item_number += 1

    if values:
        return values
    if existing:
        return existing
    return []


def _parse_value(*, node: FieldNode, raw: str) -> Any:
    if node.annotation is bool:
        lowered = raw.strip().lower()
        if lowered in {"y", "yes", "true", "1"}:
            return True
        if lowered in {"n", "no", "false", "0"}:
            return False
    if node.choices and not node.is_list:
        return _parse_choice(raw=raw, node=node)
    adapter = TypeAdapter(node.annotation)
    return adapter.validate_python(raw)


def _parse_choice(*, raw: str, node: FieldNode) -> Any:
    stripped = raw.strip()
    if stripped.isdigit():
        idx = int(stripped) - 1
        if 0 <= idx < len(node.choices):
            return node.choices[idx]
    if stripped in node.choices:
        return stripped
    raise ValueError(f"Value must be one of {', '.join(node.choices)}")


def _default_to_text(value: Any) -> str:
    if isinstance(value, bool):
        return "yes" if value else "no"
    if isinstance(value, list):
        return ",".join(str(item) for item in value)
    return str(value)


def _as_model(annotation: Any) -> type[BaseModel] | None:
    if inspect.isclass(annotation) and issubclass(annotation, BaseModel):
        return annotation
    return None
