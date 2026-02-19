# Richforms

`richforms` turns Pydantic data models into interactive Rich terminal forms.

## Features

- Required values are explicitly prompted with type hints.
- Defaulted values can be accepted without change.
- Validation failures trigger targeted repair loops.
- Works as a Python API or a thin standalone CLI.
- Integrates with Click and Typer via callback helpers.

## Install

```bash
uv add richforms
```

## CLI

```bash
# Start a new form
richforms fill richforms.example.model:Family

# Edit an existing form
richforms edit richforms.example.model:Family --from-file metadata.json

# Live cockpit redraw
richforms fill richforms.example.model:Family --live

# Force static transcript mode
richforms fill richforms.example.model:Family --no-live
```
