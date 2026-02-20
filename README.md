# richforms

`richforms` turns Pydantic models into rich interactive terminal forms.

## Installation

You can add `richforms` to your project with `uv`.

```bash
uv add richforms
```

## Usage

You can start from Python in-process or from the bundled CLI.

### Python API

```python
from richforms.example.model import Metadata
from richforms import fill


metadata = fill(Metadata)
print(metadata.model_dump_json(indent=2))
```

### CLI

```bash
richforms fill richforms.example.model:Metadata --output project-metadata.json
```

### Integrations

You can integrate `richforms` directly into Click and Typer option callbacks.

```python
import typer

from richforms.integrations.typer import form_callback
from richforms.example.model import Metadata

app = typer.Typer()


@app.command()
def release(
    metadata: Metadata = typer.Option(
        None,
        callback=form_callback(Metadata),
    ),
) -> None:
    print(metadata.model_dump())
```

## Documentation

For more information, see the [documentation](https://shinybrar.github.io/richforms/).
