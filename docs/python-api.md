# Python API

The Python API is the right entry point when you want form collection inside
your existing open source project commands, automation helpers, or tests.

## Core imports

You can import all public entry points from `richforms`.

```python title="public API"
from richforms import FormConfig, collect_dict, edit, fill, serialize_result
```

## `fill(model_type, ...)`

Use `fill` to collect values for a model type and return a validated instance.

```python title="collect a model instance"
metadata = fill(ProjectMetadata)
```

`fill` accepts optional keyword arguments.

| Parameter | Description |
| --- | --- |
| `initial` | Optional dictionary of starting values. |
| `config` | `FormConfig` for interaction and behavior overrides. |
| `console` | Optional Rich `Console` instance. |

## Exclude fields from prompts with `json_schema_extra`

You can mark fields as non-interactive while keeping them in the canonical
Pydantic model. RichForms skips excluded fields during prompt collection.

```python title="exclude system-managed fields"
from datetime import datetime
from pydantic import BaseModel, Field


class ReleaseMetadata(BaseModel):
    name: str
    version: str
    record_id: str = Field(..., json_schema_extra={"richforms": {"exclude": True}})
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        json_schema_extra={"richforms": {"exclude": True}},
    )
```

RichForms behavior for excluded fields is:

- It doesn't prompt fields with `richforms.exclude=True`.
- It still validates using the full Pydantic model.
- It succeeds when excluded fields are provided through `initial`,
  `default`, or `default_factory`.
- It raises a RichForms error when an excluded required field remains
  unresolved.

## `edit(instance, ...)`

Use `edit` to start from an existing model instance and return an updated one.

```python title="edit an instance"
updated = edit(existing_metadata)
```

This is equivalent to `fill(type(instance), initial=instance.model_dump(...))`
with internal defaults.

## `collect_dict(model_type, ...)`

Use `collect_dict` when your pipeline expects a dictionary instead of a model.

```python title="collect plain dict"
payload = collect_dict(ProjectMetadata)
```

The return value is `model.model_dump(mode="python")`.

## `serialize_result(model, ...)`

Use `serialize_result` to convert a model to JSON or YAML, with optional file
output.

```python title="serialize in memory"
text = serialize_result(metadata, format="yaml")
```

```python title="serialize to file"
serialize_result(metadata, format="json", path=Path("metadata.json"))
```

When `path` is set, the function writes to disk and returns `None`.

## FormConfig reference

`FormConfig` lets you shape interaction behavior for your project.

| Field | Type | Default | Description |
| --- | --- | --- | --- |
| `confirm_before_return` | `bool` | `True` | Ask for final confirmation before returning. |
| `save_draft_on_interrupt` | `"prompt"\|"always"\|"never"` | `"prompt"` | Control draft save behavior on keyboard interrupt. |
| `draft_directory` | `Path \| None` | `None` | Directory for interrupt draft files. |
| `clear_on_step` | `bool` | `True` | Clear terminal before each field on terminal consoles. |
| `interaction` | protocol implementation | `None` | Provide custom ask/confirm behavior. |
| `console` | `rich.console.Console` | `None` | Reuse your own console instance. |

## Deprecated aliases

Two API aliases remain available for compatibility and emit
`DeprecationWarning`.

- `collect_model(...)` -> use `fill(...)`
- `edit_model(...)` -> use `edit(...)`

!!! note
    Migrate to `fill` and `edit` in new code to avoid future breaking changes.
