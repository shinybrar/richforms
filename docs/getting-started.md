# Getting Started

This guide shows you how to install `richforms`, define a model, and run both
Python and CLI form flows. It is written for maintainers who want to add typed
input collection to an open source project quickly.

## Prerequisites

You need a Python environment that matches project requirements.

- Python 3.10 or newer.
- A project using Pydantic v2 models.
- A terminal where Rich output is supported.

## Installation

You can install `richforms` with either `uv` or `pip`.

=== "uv"

    ```bash title="add to project dependencies"
    uv add richforms
    ```

=== "pip"

    ```bash title="install from PyPI"
    pip install richforms
    ```

## Define a model

Your model is the contract that drives prompts, validation, and output.

```python title="Example model shipped with richforms"
# richforms/example/model.py
from pydantic import AnyUrl, BaseModel, Field


class Metadata(BaseModel):
    name: str = Field(
        ...,
        title="Name",
        description="Name of the project.",
        examples=["richforms"],
    )
    repository: AnyUrl = Field(
        ...,
        title="Repository",
        description="Repository URL",
        examples=["https://github.com/shinybrar/richforms"],
    )
    license: str = Field("MIT", title="License", description="SPDX license")
    version: str = Field(
        ...,
        title="Version",
        description="Version of the project.",
        examples=["0.1.0"],
    )
```

## Form Collection

### Python API

You can collect a validated model in-process and continue your workflow.

```python title="Python API"
from richforms import fill
from richforms.example.model import Metadata

metadata = fill(Metadata)
print(metadata.model_dump_json(indent=2))
```

### CLI

You can run the same model through the packaged CLI.

```bash title="Start a new form"
richforms fill richforms.example.model:Metadata
```

If you already have a payload, you can seed values from disk.

```bash title="Seed defaults from file and write YAML"
richforms fill richforms.example.model:Metadata \
  --from-file metadata.json \
  --output metadata.yaml \
  --format yaml
```

### Edit existing forms

You can load an existing document, update fields interactively, and save it.

```bash title="Edit an existing form"
richforms edit richforms.example.model:Metadata \
  --from-file metadata.yaml \
  --output metadata.yaml
```

!!! note
    `--from-file` accepts JSON, `.yaml`, or `.yml` payload files.
