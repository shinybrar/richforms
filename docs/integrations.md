# Integrations

`richforms` includes callback helpers for Click and Typer so you can add
interactive model collection without rewriting your CLI architecture.

## Click integration

You can attach `form_callback` to a Click option. If no file is supplied,
`richforms` starts an interactive session. If a file is supplied, it loads and
validates the payload.

```python title="Click callback pattern"
from pathlib import Path

import click

from richforms.integrations.click import form_callback
from your_package.models import ProjectMetadata


@click.command()
@click.option(
    "--metadata-file",
    type=click.Path(path_type=Path),
    callback=form_callback(ProjectMetadata),
)
def release(metadata_file: ProjectMetadata) -> None:
    click.echo(metadata_file.model_dump_json(indent=2))
```

## Typer integration

You can use the Typer callback helper with the same behavior.

```python title="Typer callback pattern"
from pathlib import Path

import typer

from richforms.integrations.typer import form_callback
from your_package.models import ProjectMetadata

app = typer.Typer()


@app.command()
def release(
    metadata: ProjectMetadata = typer.Option(
        None,
        callback=form_callback(ProjectMetadata),
    ),
) -> None:
    print(metadata.model_dump())
```

## Integration behavior

Both integrations share the same resolution model for option values.

1. If the option value is `None`, run an interactive `fill(...)` flow.
2. If the option value is a path, load JSON or YAML from disk.
3. Validate payload with `model_type.model_validate(...)`.
4. Return the validated model instance to your command handler.

!!! tip
    Keep your command parameter typed as the target model to get immediate
    editor support and cleaner downstream code.

## Custom behavior with FormConfig

You can pass a custom `FormConfig` if you need project-specific interaction
behavior, such as custom prompt handlers in tests.

```python title="custom interaction config"
from richforms.config import FormConfig
from richforms.integrations.click import form_callback

callback = form_callback(ProjectMetadata, config=FormConfig(clear_on_step=False))
```
