from __future__ import annotations

from copy import deepcopy
from typing import Any


def copy_initial(initial: dict[str, Any] | None) -> dict[str, Any]:
    return deepcopy(initial) if initial else {}


def path_parts(path: str) -> list[str]:
    return [part for part in path.split(".") if part]


def has_nested_value(data: dict[str, Any], path: str) -> bool:
    parts = path_parts(path)
    current: Any = data
    for part in parts:
        if not isinstance(current, dict) or part not in current:
            return False
        current = current[part]
    return True


def get_nested_value(data: dict[str, Any], path: str) -> Any:
    parts = path_parts(path)
    current: Any = data
    for part in parts:
        if not isinstance(current, dict) or part not in current:
            raise KeyError(path)
        current = current[part]
    return current


def set_nested_value(data: dict[str, Any], path: str, value: Any) -> None:
    parts = path_parts(path)
    current: Any = data
    for part in parts[:-1]:
        if part not in current or not isinstance(current[part], dict):
            current[part] = {}
        current = current[part]
    current[parts[-1]] = value
