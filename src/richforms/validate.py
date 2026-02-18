from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel, ValidationError


@dataclass(slots=True)
class ValidationResult:
    model: BaseModel | None
    errors: dict[str, str]


def validate_draft(model_type: type[BaseModel], draft: dict[str, Any]) -> ValidationResult:
    try:
        model = model_type.model_validate(draft)
    except ValidationError as exc:
        errors: dict[str, str] = {}
        for error in exc.errors():
            path = _loc_to_path(error.get("loc", ()))
            errors[path] = str(error.get("msg", "Invalid value"))
        return ValidationResult(model=None, errors=errors)
    return ValidationResult(model=model, errors={})


def _loc_to_path(loc: tuple[Any, ...] | list[Any]) -> str:
    parts: list[str] = []
    for item in loc:
        if isinstance(item, str):
            parts.append(item)
    return ".".join(parts) if parts else "__root__"
