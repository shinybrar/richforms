from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_payload_file(path: Path) -> dict[str, Any]:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ValueError(f"Could not read payload file {path}: {exc.strerror or exc}") from exc
    if path.suffix.lower() in {".yaml", ".yml"}:
        import yaml

        try:
            data = yaml.safe_load(text)
        except yaml.YAMLError as exc:
            raise ValueError(f"Invalid YAML in {path}: {exc}") from exc
    else:
        try:
            data = json.loads(text)
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"Invalid JSON in {path}: {exc.msg} at line {exc.lineno}, column {exc.colno}"
            ) from exc
    if not isinstance(data, dict):
        raise ValueError(f"Expected object payload in {path}, got {type(data).__name__}")
    return data
