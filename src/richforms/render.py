from __future__ import annotations

from collections.abc import Iterable

from pydantic import BaseModel
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from richforms.schema import FieldNode


def render_field_card(
    *,
    node: FieldNode,
    index: int,
    total: int,
    current_path: str,
    error: str | None = None,
    has_default: bool = False,
    default_value: object | None = None,
) -> Panel:
    field_label = node.title or node.name
    optional_hint = "Press Enter to continue without a value."
    body = Text()
    body.append(f"Path: {current_path}\n", style="bold cyan")
    body.append(f"Field: {field_label}\n")
    body.append(f"Type: {node.type_label}\n")
    body.append(f"Required: {'yes' if node.required else 'no'}\n")
    if has_default:
        body.append(f"Default: {default_value!r}\n")
    if not node.required:
        body.append(f"{optional_hint}\n")
    if node.description:
        body.append(f"\n{node.description}\n")
    if node.examples:
        body.append(f"Examples: {node.examples}\n")
    if node.choices:
        body.append(f"Choices: {', '.join(node.choices)}\n")
    if error:
        body.append(f"\nValidation: {error}\n", style="bold red")

    return Panel(
        body,
        title=f"Field {index}/{total}",
        subtitle=node.title or node.name,
        border_style="cyan",
    )


def render_path_radar(
    nodes: Iterable[FieldNode],
    *,
    current_path: str,
    path_prefix: str = "",
    completed_paths: set[str] | None = None,
    error_paths: set[str] | None = None,
) -> Panel:
    completed_paths = completed_paths or set()
    error_paths = error_paths or set()
    table = Table(show_header=True, header_style="bold")
    table.add_column("Status", width=8)
    table.add_column("Path")
    for node in nodes:
        display_path = f"{path_prefix}.{node.path}" if path_prefix else node.path
        status = Text("·", style="grey50")
        marker = Text("●", style="bold cyan") if node.required else Text("○", style="grey50")
        if display_path == current_path:
            status = Text("→", style="bold cyan")
        elif display_path in error_paths:
            status = Text("!", style="bold red")
        elif display_path in completed_paths:
            status = Text("✓", style="bold green")
        table.add_row(status, Text.assemble(marker, " ", display_path))
    return Panel(table, title="Path Radar", border_style="grey50")


def render_validation_ledger(errors: dict[str, str]) -> Panel:
    table = Table(show_header=True, header_style="bold red")
    table.add_column("Path")
    table.add_column("Error")
    for path, message in errors.items():
        table.add_row(path, message)
    return Panel(table, title="Validation Ledger", border_style="red")


def render_review(model: BaseModel) -> Panel:
    table = Table(show_header=True, header_style="bold green")
    table.add_column("Path")
    table.add_column("Value")
    for key, value in model.model_dump(mode="python").items():
        table.add_row(key, repr(value))
    return Panel(table, title="Review", border_style="green")
