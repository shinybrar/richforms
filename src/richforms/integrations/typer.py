from __future__ import annotations

from pathlib import Path
from typing import TypeVar

from pydantic import BaseModel

from richforms.config import FormConfig
from richforms.integrations.click import form_callback as click_form_callback

T = TypeVar("T", bound=BaseModel)


def form_callback(model_type: type[T], *, config: FormConfig | None = None):
    callback = click_form_callback(model_type, config=config)

    def _callback(value: Path | None) -> T:
        return callback(None, None, value)

    return _callback
