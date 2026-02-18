from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import BaseModel

from richforms.exceptions import SerializationError

Format = Literal["json", "yaml"]


def serialize_result(model: BaseModel, *, format: Format, path: Path | None = None) -> str | None:
    if format == "json":
        payload = model.model_dump_json(indent=2)
    elif format == "yaml":
        payload = _to_yaml(model)
    else:
        raise SerializationError(f"Unsupported serialization format: {format}")

    if path is not None:
        path.write_text(payload, encoding="utf-8")
        return None
    return payload


def _to_yaml(model: BaseModel) -> str:
    try:
        import yaml
    except ImportError as exc:  # pragma: no cover - guarded by dependency
        raise SerializationError(
            "YAML serialization requires pyyaml. Install richforms[yaml]."
        ) from exc
    return yaml.safe_dump(model.model_dump(mode="json"), sort_keys=False)
