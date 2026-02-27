from __future__ import annotations

import inspect
from typing import Any

from pydantic import BaseModel, TypeAdapter, ValidationError
from rich.console import Console

from richforms.config import FormConfig, Interaction
from richforms.schema import FieldNode

_CLEAR_TOKENS = {"-", "null", "none"}
_LIST_ITEM_PROMPT_HINT = "(↵ to finish, - to reset)"


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
        default_text = None
        if has_default and not (default_value is None and not node.required):
            default_text = _default_to_text(default_value)
        prompt = prompt_path
        if has_default and not node.required:
            prompt = f"{prompt_path} (Press Enter to keep current value, '-' to clear.)"
        elif not node.required:
            prompt = f"{prompt_path} ({optional_hint})"
        raw = interaction.ask(prompt, default=default_text)
        if raw == "" and has_default:
            return default_value
        if raw == "" and not node.required:
            return None
        if _is_clear_token(raw):
            if node.required:
                console.print(f"[red]{prompt_path} is required and cannot be cleared.[/red]")
                continue
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
        decision_prompt = _default_edit_prompt(prompt_path=prompt_path, default_value=default_value)
        while True:
            normalized = interaction.choose(
                decision_prompt,
                choices={"e", "-"},
                default="",
            )
            if normalized == "":
                return list(default_value)
            if normalized == "e":
                break
            if _is_clear_token(normalized):
                return []
            console.print(
                "[red]Choose one: press Enter to keep, type 'e' to edit, or '-' to clear.[/red]"
            )

    item_adapter = TypeAdapter(item_annotation)
    values: list[Any] = []
    index = 1
    while True:
        prompt = f"{prompt_path}[{index}] {_LIST_ITEM_PROMPT_HINT}"
        raw = interaction.ask(prompt)
        if _is_clear_token(raw):
            values = []
            index = 1
            continue
        if raw == "":
            if index == 1:
                return []
            break
        try:
            values.append(item_adapter.validate_python(raw))
        except ValidationError as exc:
            message = f"Invalid value for {prompt_path}: {exc.errors()[0]['msg']}"
            console.print(f"[red]{message}[/red]")
            continue
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
    if existing:
        decision_prompt = _default_edit_prompt(prompt_path=prompt_path, default_value=default_value)
        while True:
            normalized = interaction.choose(
                decision_prompt,
                choices={"e", "-"},
                default="",
            )
            if normalized == "":
                return existing
            if normalized == "e":
                break
            if _is_clear_token(normalized):
                return []
            console.print(
                "[red]Choose one: press Enter to keep, type 'e' to edit, or '-' to clear.[/red]"
            )

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
        from richforms.api import fill

        child_config = FormConfig(
            interaction=interaction,
            console=console,
            confirm_before_return=False,
        )
        item = fill(
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


def _default_edit_prompt(*, prompt_path: str, default_value: Any) -> str:
    return (
        f"{prompt_path} [bold]Default:[/bold] {repr(default_value)}: "
        "[bold yellow]e[/bold yellow] to edit, [bold red]-[/bold red] to clear, "
        "[bold]↵[/bold] to continue"
    )


def _as_model(annotation: Any) -> type[BaseModel] | None:
    if inspect.isclass(annotation) and issubclass(annotation, BaseModel):
        return annotation
    return None


def _is_clear_token(raw: str) -> bool:
    return raw.strip().lower() in _CLEAR_TOKENS
