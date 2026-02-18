# Integrations

## Click callback helper

```python
import click
from richforms.integrations.click import form_callback


@click.command()
@click.option("--metadata-file", type=click.Path(path_type=Path), callback=form_callback(Metadata))
def cmd(metadata_file):
    metadata = metadata_file
    ...
```

Behavior:

- When option value is missing, `richforms` launches interactive collection.
- When value is provided, payload is loaded and validated directly.

## Typer callback helper

```python
import typer
from pathlib import Path
from richforms.integrations.typer import form_callback

app = typer.Typer()


@app.command()
def run(metadata: Path | None = typer.Option(None, callback=form_callback(Metadata))):
    model = metadata
    ...
```
