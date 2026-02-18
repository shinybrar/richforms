from __future__ import annotations

from pathlib import Path
from typing import Any, TypeVar

from pydantic import BaseModel

from richforms.api import collect_model
from richforms.config import FormConfig
from richforms.io import load_payload_file

T = TypeVar("T", bound=BaseModel)


def form_callback(model_type: type[T], *, config: FormConfig | None = None):
    def _callback(ctx: Any, param: Any, value: Path | str | None) -> T:
        del ctx, param
        if value is None:
            return collect_model(model_type, config=config)
        path = value if isinstance(value, Path) else Path(value)
        payload = load_payload_file(path)
        return model_type.model_validate(payload)

    return _callback
