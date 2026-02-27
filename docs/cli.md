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
| `--format` | `json|yaml` | Serialization format for output. Defaults to output file extension when recognized (`.json`, `.yaml`, `.yml`), otherwise `json`. |
| `--clear / --no-clear` | `bool` | Toggle terminal clear between fields. |

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
| `--format` | `json|yaml` | Serialization format for output. Defaults to output file extension when recognized (`.json`, `.yaml`, `.yml`), otherwise `json`. |
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
- For optional fields with existing values, pressing Enter keeps the value and typing `-` clears it.
- For list fields with existing values, press Enter to keep, press `e` to edit, or press `-` to clear (single-key input on terminal sessions).
- While entering scalar list items, keep typing values; press `↵` to finish or press `-` to reset the current list edit session.
- If `--format` conflicts with `--output` suffix, RichForms writes the requested format and prints a warning.

If a field is annotated with
`json_schema_extra={"richforms": {"exclude": True}}`, RichForms skips that
prompt. Excluded required fields must still resolve through initial values or
Pydantic defaults, or RichForms exits with a clear validation error.

## CLI walkthrough for excluded fields

You can use the bundled `ExcludedFieldExample` model to see excluded prompt
fields in action.

1. Run `fill` with the example model.

```bash title="collect payload with excluded fields"
richforms fill richforms.example.model:ExcludedFieldExample --output excluded-example.json
```

2. Enter values for only the prompted fields.

```text title="prompt flow"
name: Release Metadata
version: 1.2.3
```

3. Review the output file. RichForms keeps excluded fields on the model, but
   it never prompts for them.

```json title="excluded-example.json"
{
  "name": "Release Metadata",
  "version": "1.2.3",
  "revision": 1,
  "system_owner": "release-bot"
}
```
