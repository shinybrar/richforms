from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

MISSING = object()


@dataclass(slots=True)
class FieldNode:
    path: str
    name: str
    title: str | None
    description: str | None
    examples: list[Any]
    required: bool
    annotation: Any
    type_label: str
    has_default: bool
    default: Any = MISSING
    choices: list[str] = field(default_factory=list)
    is_list: bool = False
    item_annotation: Any | None = None


@dataclass(slots=True)
class ModelSchema:
    model_name: str
    leaf_nodes: list[FieldNode]
    excluded_paths: set[str] = field(default_factory=set)

    @property
    def by_path(self) -> dict[str, FieldNode]:
        return {node.path: node for node in self.leaf_nodes}
