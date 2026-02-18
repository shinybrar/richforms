from __future__ import annotations

import inspect
from enum import Enum
from typing import Any, Literal, Union, get_args, get_origin

from pydantic import BaseModel

from richforms.schema import MISSING, FieldNode, ModelSchema


def build_model_schema(model_type: type[BaseModel]) -> ModelSchema:
    nodes: list[FieldNode] = []
    _walk_model(model_type=model_type, prefix="", nodes=nodes)
    return ModelSchema(model_name=model_type.__name__, leaf_nodes=nodes)


def _walk_model(model_type: type[BaseModel], prefix: str, nodes: list[FieldNode]) -> None:
    for name, field in model_type.model_fields.items():
        path = f"{prefix}.{name}" if prefix else name
        annotation = _unwrap_optional(field.annotation)
        nested = _as_model(annotation)
        if nested is not None:
            _walk_model(nested, path, nodes)
            continue

        has_default, default = _extract_default(field)
        choices = _extract_choices(annotation)
        item_annotation = None
        is_list = _is_list(annotation)
        if is_list:
            item_annotation = _list_item(annotation)
            nested_item_choices = _extract_choices(item_annotation)
            if nested_item_choices:
                choices = nested_item_choices

        nodes.append(
            FieldNode(
                path=path,
                name=name,
                title=field.title,
                description=field.description,
                examples=list(field.examples or []),
                required=field.is_required(),
                annotation=annotation,
                type_label=_type_label(annotation),
                has_default=has_default,
                default=default,
                choices=choices,
                is_list=is_list,
                item_annotation=item_annotation,
            )
        )


def _extract_default(field: Any) -> tuple[bool, Any]:
    if field.is_required():
        return False, MISSING
    if field.default_factory is not None:
        return True, field.default_factory()
    return True, field.default


def _is_list(annotation: Any) -> bool:
    return get_origin(annotation) is list


def _list_item(annotation: Any) -> Any | None:
    args = get_args(annotation)
    if not args:
        return None
    return _unwrap_optional(args[0])


def _extract_choices(annotation: Any) -> list[str]:
    origin = get_origin(annotation)
    if origin is Literal:
        return [str(value) for value in get_args(annotation)]
    enum_type = _as_enum(annotation)
    if enum_type is not None:
        return [str(member.value) for member in enum_type]
    return []


def _unwrap_optional(annotation: Any) -> Any:
    origin = get_origin(annotation)
    if origin is Union:
        args = [arg for arg in get_args(annotation) if arg is not type(None)]
        if len(args) == 1:
            return args[0]
    return annotation


def _as_model(annotation: Any) -> type[BaseModel] | None:
    if inspect.isclass(annotation) and issubclass(annotation, BaseModel):
        return annotation
    return None


def _as_enum(annotation: Any) -> type[Enum] | None:
    if inspect.isclass(annotation) and issubclass(annotation, Enum):
        return annotation
    return None


def _type_label(annotation: Any) -> str:
    origin = get_origin(annotation)
    if origin is list:
        args = get_args(annotation)
        item = args[0] if args else Any
        return f"list[{_type_label(item)}]"
    if origin is Literal:
        return "Literal"
    if inspect.isclass(annotation):
        return annotation.__name__
    return str(annotation)
