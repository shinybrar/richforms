# richforms

`richforms` turns Pydantic models into interactive Rich terminal forms.

## Features

- Required values are explicitly prompted with type hints.
- Defaulted values can be accepted with Enter.
- Validation failures trigger targeted repair loops (only invalid fields re-prompt).
- Works as a Python API and a thin CLI.
- Integrates with Click and Typer via callback helpers.

## Install

```bash
uv add richforms
```

## CLI

```bash
richforms fill package.models:Metadata
richforms edit package.models:Metadata --from-file metadata.json
```

## Development

```bash
uv sync --dev
uv run ruff format --check .
uv run ruff check .
uv run ty check .
uv run pytest -q
```
