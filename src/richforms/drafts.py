from __future__ import annotations

from datetime import datetime
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any

import yaml


def default_draft_directory() -> Path:
    return Path.cwd() / ".richforms-drafts"


def build_draft_path(model_name: str, *, directory: Path | None = None) -> Path:
    root = directory or default_draft_directory()
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    stem = _safe_model_stem(model_name)
    return root / f"{stem}-{timestamp}.yaml"


def save_draft_yaml(draft: dict[str, Any], *, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        dir=path.parent,
        prefix=f".{path.stem}.",
        suffix=".tmp",
        delete=False,
    ) as tmp:
        yaml.safe_dump(draft, tmp, sort_keys=False)
        tmp_path = Path(tmp.name)
    tmp_path.replace(path)


def _safe_model_stem(model_name: str) -> str:
    lowered = model_name.lower()
    safe = "".join(ch if ch.isalnum() else "-" for ch in lowered)
    return "-".join(part for part in safe.split("-") if part) or "model"
