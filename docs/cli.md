# CLI guide

The `richforms` CLI gives you a fast way to collect or update model-backed
payloads in scripts, release workflows, and local maintainer tooling.

## Command summary

You run the top-level command and then choose `fill` or `edit`.

```bash title="list commands"
richforms --help
```

| Command | Purpose | Required input |
| --- | --- | --- |
| `richforms fill MODEL` | Create a new payload interactively. | `MODEL` path (`module:ModelName`) |
| `richforms edit MODEL` | Edit an existing payload interactively. | `MODEL` path and `--from-file` |

## Fill command

Use `fill` when you need to create a new model instance from scratch or from
partial defaults.

```bash title="Create JSON output"
richforms fill richforms.example.model:Metadata --output metadata.json
```

You can pass starter values from an existing file.

```bash title="Seed defaults from YAML"
richforms fill richforms.example.model:Metadata \
  --from-file metadata.yaml \
  --output metadata.yaml
```

### Fill options

You can combine these options based on your workflow.

| Option | Type | Description |
| --- | --- | --- |
| `--from-file` | `Path` | Optional JSON or YAML file used as initial values. |
| `--output` | `Path` | Writes result to the target file. |
| `--format` | `json|yaml` | Serialization format for output. Default is `json`. |
| `--clear / --no-clear` | `bool` |Toggle terminal clear between fields. |

## Edit command

Use `edit` when you already have a valid payload and want to change it safely.

```bash title="edit existing payload"
richforms edit richforms.example.model:Metadata \
  --from-file metadata.json \
  --output metadata.json
```

### Edit options

The option set is similar to `fill`, but `--from-file` is required.

| Option | Type | Description |
| --- | --- | --- |
| `--from-file` | `PATH` | Required source JSON or YAML payload. |
| `--output` | `PATH` | Writes result to the target file. |
| `--format` | `json|yaml` | Serialization format for output. Default is `json`. |
| `--clear / --no-clear` | `bool` | Toggle terminal clear between fields. |

!!! warning
    `MODEL` must be in `module:ModelName` format. If not, the command exits
    with a parameter error.

## Behavior details

The CLI shares the same validation behavior as the Python API.

- It prompts every eligible leaf field during first pass.
- It validates using the full model after each pass.
- It re-prompts only fields that failed validation.
- It asks for final submission confirmation before returning output.

If a field is annotated with
`json_schema_extra={"richforms": {"exclude": True}}`, RichForms skips that
prompt. Excluded required fields must still resolve through initial values or
Pydantic defaults, or RichForms exits with a clear validation error.
