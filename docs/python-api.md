# Python API

## Core entry points

```python
from richforms import fill, edit, collect_dict, serialize_result
```

### `fill`

```python
fill(
    model_type,
    *,
    initial: dict | None = None,
    config: FormConfig | None = None,
    console: Console | None = None,
)
```

Returns a validated Pydantic model instance.

### `edit`

```python
edit(instance, *, config=None, console=None)
```

Uses an existing instance as interactive defaults.

### `collect_dict`

```python
collect_dict(model_type, *, initial=None, config=None, console=None)
```

Returns the validated model as a Python dictionary.

### `serialize_result`

```python
serialize_result(model, *, format="json" | "yaml", path=None)
```

- Returns a string when `path=None`.
- Writes to disk and returns `None` when `path` is provided.

### Deprecated aliases

`collect_model` and `edit_model` remain available temporarily and emit a
`DeprecationWarning`. Prefer `fill` and `edit`.
