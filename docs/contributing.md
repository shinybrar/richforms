# Contributing

## Setup

```bash
uv sync --dev
pre-commit install
```

## Required checks

```bash
uv run ruff format --check .
uv run ruff check .
uv run ty check .
uv run pytest -q
```

All checks must pass before merge.

## Test expectations

- Unit tests for schema extraction, parsing, and serialization.
- Interaction tests for repair loops and default handling.
- Integration tests for CLI and Click/Typer callback behavior.
