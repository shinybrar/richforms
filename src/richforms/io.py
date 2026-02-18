from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_payload_file(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() in {".yaml", ".yml"}:
        import yaml

        data = yaml.safe_load(text)
    else:
        data = json.loads(text)
    if not isinstance(data, dict):
        raise ValueError(f"Expected object payload in {path}, got {type(data).__name__}")
    return data
