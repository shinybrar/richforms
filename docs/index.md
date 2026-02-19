# RichForms

`richforms` turns Pydantic data models into interactive Rich terminal forms.

## Why

- Prompt required values with visible type hints.
- Let users hit Enter to accept defaults.
- Re-prompt only invalid fields after validation.
- Reuse the same model contracts across Python API, CLI, and Click/Typer apps.

## Interface signature

The UI is built around three persistent views:

- **Waypoint Tree**: full nested path context with explicit state markers and legend (`→ ✓ ! · ● ○`).
- **Field Dossier**: title, description, type, required/default context, examples.
- **Validation Logbook**: only invalid paths and their latest errors.

## Quick example

```python
from richforms import fill
from my_models import Metadata

metadata = fill(Metadata)
print(metadata.model_dump_json(indent=2))
```
