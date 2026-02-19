# Getting Started

## Install

```bash
uv add richforms
```

## Build a form from a model

```python
from pydantic import BaseModel, Field
from richforms import fill


class ImageMetadata(BaseModel):
    title: str = Field(..., description="Human-readable title")
    source: str = Field(..., description="Source repository URL")
    deprecated: bool = False


metadata = fill(ImageMetadata)
```

## Behavior

- Required fields are always requested.
- Defaulted fields accept Enter.
- Validation runs on the full payload.
- Only failing fields are re-requested in repair loops.
