# richforms

`richforms` generates interactive terminal forms from Pydantic models.

## Why

- Prompt required values with visible type hints.
- Let users hit Enter to accept defaults.
- Re-prompt only invalid fields after validation.
- Reuse the same model contracts across Python API, CLI, and Click/Typer apps.

## Interface signature

The UI is built around three persistent views:

- **Path Radar**: where you are (`metadata.discovery.source`) and what remains.
- **Field Card**: title, description, type, required/default context, examples.
- **Validation Ledger**: only invalid paths and their latest errors.

## Quick example

```python
from richforms import collect_model
from my_models import Metadata

metadata = collect_model(Metadata)
print(metadata.model_dump_json(indent=2))
```
