from __future__ import annotations

from collections.abc import Iterable
from pprint import pformat

from pydantic import BaseModel
from rich import box
from rich.console import Group, RenderableType
from rich.rule import Rule
from rich.table import Table
from rich.text import Text
from rich.tree import Tree

from richforms.schema import FieldNode


def render_editor_view(
    *,
    nodes: Iterable[FieldNode],
    node: FieldNode,
    index: int,
    total: int,
    current_path: str,
    error: str | None = None,
    has_default: bool = False,
    default_value: object | None = None,
    path_prefix: str = "",
    completed_paths: set[str] | None = None,
    error_paths: set[str] | None = None,
    console_width: int = 120,
) -> RenderableType:
    node_list = list(nodes)
    n_completed = len(completed_paths or set())
    n_errors = len(error_paths or set())
    progress = Text.assemble(
        ("Field ", "bold"),
        (f"{index}/{total}", "bold cyan"),
        ("  ·  ", "grey50"),
        (f"{n_completed}/{len(node_list)} done", "bold green"),
        ("  ·  ", "grey50"),
        (f"{n_errors} errors", "bold red" if n_errors else "grey50"),
    )
    waypoint = render_path_radar(
        nodes=node_list,
        current_path=current_path,
        path_prefix=path_prefix,
        completed_paths=completed_paths,
        error_paths=error_paths,
    )
    dossier = render_field_card(
        node=node,
        index=index,
        total=total,
        current_path=current_path,
        error=error,
        has_default=has_default,
        default_value=default_value,
    )
    return Group(
        progress,
        Text(),
        waypoint,
        Text(),
        dossier,
        Text(),
    )


def render_field_card(
    *,
    node: FieldNode,
    index: int,
    total: int,
    current_path: str,
    error: str | None = None,
    has_default: bool = False,
    default_value: object | None = None,
) -> Group:
    field_label = node.title or node.name
    table = Table.grid(padding=(0, 1))
    table.add_column(style="bold grey70", no_wrap=True, width=18)
    table.add_column(ratio=1)
    table.add_row("Path", Text(current_path, style="bold cyan"))
    table.add_row("Field", field_label)
    table.add_row("Required", "yes" if node.required else "no")
    table.add_row("Type", _code_label(node.type_label))
    if node.description:
        table.add_row("Description", node.description)
    if node.examples:
        table.add_row("Examples", _code_label(pformat(node.examples, width=60)))
    if node.choices:
        table.add_row("Choices", ", ".join(node.choices))
    if error:
        table.add_row("Validation", Text(error, style="bold red"))

    return Group(Rule(f"Field Dossier · {field_label}", style="grey42"), table)


def render_path_radar(
    nodes: Iterable[FieldNode],
    *,
    current_path: str,
    path_prefix: str = "",
    completed_paths: set[str] | None = None,
    error_paths: set[str] | None = None,
) -> Group:
    completed_paths = completed_paths or set()
    error_paths = error_paths or set()
    tree = Tree("root", guide_style="grey35", hide_root=True)
    branch_map: dict[str, Tree] = {"": tree}
    for node in nodes:
        display_path = f"{path_prefix}.{node.path}" if path_prefix else node.path
        parts = display_path.split(".")
        parent_key = ""
        for idx, part in enumerate(parts):
            key = ".".join(parts[: idx + 1])
            parent = branch_map[parent_key]
            if key not in branch_map:
                is_leaf = idx == len(parts) - 1
                if is_leaf:
                    state = Text("·", style="grey50")
                    if node.required:
                        marker = Text("●", style="bold cyan")
                    else:
                        marker = Text("○", style="grey60")
                    if key == current_path:
                        state = Text("→", style="bold cyan")
                    elif key in error_paths:
                        state = Text("!", style="bold red")
                    elif key in completed_paths:
                        state = Text("✓", style="bold green")
                    label = Text.assemble(state, " ", marker, f" {part}")
                else:
                    label = Text(part, style="bold grey70")
                branch_map[key] = parent.add(label)
            parent_key = key
    legend = Text.assemble(
        ("Legend: ", "bold"),
        ("→ current  ", "bold cyan"),
        ("✓ done  ", "bold green"),
        ("! error  ", "bold red"),
        ("· pending  ", "grey50"),
        ("● required  ", "bold cyan"),
        ("○ optional", "grey60"),
    )
    return Group(Rule("Waypoint Tree", style="grey42"), tree, Text(), legend)


def render_validation_ledger(errors: dict[str, str]) -> Group:
    table = Table(show_header=True, header_style="bold red", box=box.MINIMAL, pad_edge=False)
    table.add_column("Path")
    table.add_column("Error")
    for path, message in errors.items():
        table.add_row(path, message)
    return Group(Rule("Validation Errors", style="red"), table)


def render_review(model: BaseModel) -> Group:
    table = Table(show_header=True, header_style="bold green", box=box.MINIMAL, pad_edge=False)
    table.add_column("Path")
    table.add_column("Value")
    for key, value in model.model_dump(mode="python").items():
        table.add_row(key, repr(value))
    return Group(Rule("Review", style="green"), table)


def _code_label(value: str) -> Text:
    """Return a styled text label visible on both light and dark terminals."""
    return Text(value, style="bold")
